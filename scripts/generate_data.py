import csv
import random
from faker import Faker

fake = Faker(["en_US", "en_CA", "fr_CA"])

OUTPUT_FILE = "scripts/mock_data.csv"
TOTAL_RECORDS = 1200
INVALID_RATIO = 0.15

FIELDNAMES = ["full_name", "email", "phone_number"]


def generate_valid_record() -> dict:
    return {
        "full_name": fake.name(),
        "email": fake.email(),
        "phone_number": fake.numerify("###-###-####"),
    }


def generate_invalid_record() -> dict:
    invalid_type = random.choice(["name", "email", "phone", "multiple"])

    record = generate_valid_record()

    if invalid_type == "name":
        record["full_name"] = random.choice([
            fake.first_name(),                                              # single name, no last name
            fake.name() + "123",                                            # contains numbers
            fake.name() + "@#$",                                            # contains special characters
        ])
    elif invalid_type == "email":
        record["email"] = random.choice([
            fake.first_name(),                                              # no @ symbol
            fake.first_name() + "@",                                        # missing domain
            "notanemail",                                                   # completely invalid
        ])
    elif invalid_type == "phone":
        record["phone_number"] = random.choice([
            "123",                                                          # too short
            "abcd-efg-hijk",                                                # letters
            "00000000000000",                                               # too long
        ])
    elif invalid_type == "multiple":
        record["full_name"] = fake.first_name()
        record["email"] = "notanemail"
        record["phone_number"] = "123"

    return record


def main() -> None:
    invalid_count = int(TOTAL_RECORDS * INVALID_RATIO)
    valid_count = TOTAL_RECORDS - invalid_count

    records = (
        [generate_valid_record() for _ in range(valid_count)]
        + [generate_invalid_record() for _ in range(invalid_count)]
    )

    random.shuffle(records)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)

    print(f"Generated {TOTAL_RECORDS} records ({valid_count} valid, "
          f"{invalid_count} invalid) -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()