import csv
from dataclasses import dataclass

from scourgify import normalize_address_record


@dataclass
class AddressLine:
    attendees: list[str]
    street_address_1: str
    street_address_2: str
    city: str
    state: str
    postal_code: str
    email: str
    country: str = "USA"

    def to_output_dict(self) -> dict[str, str]:
        return {
            "Guest name (required)": " & ".join(self.attendees),
            "Phone number": "",
            "Email (Optional)": self.email,
            "Street Address 1": self.street_address_1,
            "Street Address 2 (Optional)": self.street_address_2 or "",
            "City": self.city,
            "State/Region": self.state,
            "Zip/Postal Code": self.postal_code,
        }


NAME = "Name"
CERTAINTY = "Certainty"
EMAIL = "Email"
ADDRESS = "Address"


def parse_csv(reader: csv.DictReader) -> list[AddressLine]:
    address_lines: list[AddressLine] = []
    last_address_line: AddressLine | None = None
    for row in reader:

        # sanitize the fields
        row = {k: v.strip() for k, v in row.items()}

        # skip maybes
        if row[CERTAINTY] != "Yes":
            continue

        # skip incomplete rows
        if not row.get(ADDRESS):
            print(f"Skipping {row[NAME]} with blank address")
            continue

        # bundle up "--" to the row above
        if last_address_line is not None and row[ADDRESS] == "—":
            last_address_line.attendees.append(row[NAME])
            continue

        # create a new AddressLine
        if last_address_line is None or row[ADDRESS] != "—":

            # flush out the last_address_line
            if last_address_line is not None:
                address_lines.append(last_address_line)

            try:
                address = normalize_address_record(row[ADDRESS].replace("\n", ","))
            except:
                # we don't care about addresses for RSVPs
                address = {
                    "address_line_1": "",
                    "address_line_2": "",
                    "city": "",
                    "state": "",
                    "postal_code": "",
                }
            last_address_line = AddressLine(
                attendees=[row[NAME]],
                street_address_1=address["address_line_1"],
                street_address_2=address["address_line_2"],
                city=address["city"],
                state=address["state"],
                postal_code=address["postal_code"],
                email=row[EMAIL],
            )
    if last_address_line is None:
        raise Exception("No AddressLines created for sheet")

    address_lines.append(last_address_line)
    return address_lines


def write_address_lines(address_lines: list[AddressLine], filename: str):
    with open(filename, "w") as fileout:
        writer = csv.DictWriter(
            fileout, fieldnames=address_lines[0].to_output_dict().keys()
        )
        writer.writeheader()
        for address_line in address_lines:
            writer.writerow(address_line.to_output_dict())


if __name__ == "__main__":
    csvs = [
        "Guests - Family RG.csv",
        "Guests - Family MG.csv",
        "Guests - Friends.csv",
        "Guests - Fam Friends.csv",
    ]
    address_lines: list[AddressLine] = []
    for sheet_name in csvs:
        with open(sheet_name) as sheet_file:
            dialect = csv.Sniffer().sniff(sheet_file.read(1024))
            sheet_file.seek(0)
            reader = csv.DictReader(sheet_file, dialect=dialect)
            address_lines.extend(parse_csv(reader))
    write_address_lines(address_lines, "output.csv")
    print(f"Number of address lines: {len(address_lines)}")
    print(f"Number of people: {sum(len(a.attendees) for a in address_lines)}")
