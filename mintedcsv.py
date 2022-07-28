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
    postal_code: int
    email: str
    country: str = "USA"

    def to_output_dict(self) -> dict[str, str]:
        return {
            "Name on Envelope": ' & '.join(self.attendees),
            "Street Address 1": self.street_address_1,
            "Street Address 2 (Optional)": self.street_address_2 or "",
            "City": self.city,
            "State/Region": self.state,
            "Zip/Postal Code": str(self.postal_code),
            "Country": self.country,
            "Email (Optional)": self.email,
            "Phone (Optional)": "",
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

        # skip incomplete rows
        if not row.get(ADDRESS):
            continue

        # skip maybes
        if row[CERTAINTY] != "Yes":
            continue

        # bundle up "--" to the row above
        if last_address_line is not None and row[ADDRESS] == "—":
            last_address_line.attendees.append(row[NAME])
            continue

        if last_address_line is None or row[ADDRESS] != "—":

            # flush out the last_address_line
            if last_address_line is not None:
                address_lines.append(last_address_line)

            address = normalize_address_record(row[ADDRESS])
            last_address_line = AddressLine(
                attendees=[row[NAME]],
                street_address_1=address["address_line_1"],
                street_address_2=address["address_line_2"],
                city=address["city"],
                state=address["state"],
                postal_code=address["postal_code"],
                email=row[EMAIL]
            )
    address_lines.append(last_address_line)
    return address_lines


def write_address_lines(address_lines: list[AddressLine], filename: str):
    with open(filename, 'w') as fileout:
        writer = csv.DictWriter(fileout, fieldnames=address_lines[0].to_output_dict().keys())
        writer.writeheader()
        for address_line in address_lines:
            writer.writerow(address_line.to_output_dict())


if __name__ == "__main__":
    csvs = ["Guests - Friends.tsv"]
    for sheet_name in csvs:
        address_lines: list[AddressLine] = []
        with open(sheet_name) as sheet_file:
            dialect = csv.Sniffer().sniff(sheet_file.read(1024))
            sheet_file.seek(0)
            reader = csv.DictReader(sheet_file, dialect=dialect)
            address_lines.extend(parse_csv(reader))
    write_address_lines(address_lines, "output.csv")
