import hashlib
import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass(slots=True, frozen=True)
class VacancyEntity:
    """A data transfer object representing a single vacancy.

    Attributes:
        title (str): The job title.
        company (str): The name of the employer.
        salary (str): Salary range or specific amount.
        experience (str): Required work experience.
        description (str): Combined responsibilities and requirements.
        link (str): URL to the full vacancy description.
        location (str): Geographical location including metro stations.
        date (str): The timestamp when the vacancy was parsed.
    """

    title: str
    company: str
    salary: str
    experience: str
    description: str
    link: str
    location: str
    date: str

    @property
    def hash(self) -> str:
        """Generates a unique SHA-256 fingerprint for the vacancy.

        The hash is based on the core content (title, company, salary,
        experience, and description).
        Metadata like 'link', 'location', or 'date' is excluded
        to ensure duplicates are detected even if posted under different URLs.

        Returns:
            str: Hexadecimal SHA-256 hash string.
        """
        payload: str = "|".join([
            self.title,
            self.company,
            self.salary,
            self.experience,
            self.description,
        ])
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_json(self) -> bytes:
        """Returns a JSON-compatible representation of the VacancyEntity.

        Returns:
            bytes: JSON-encoded string.
        """
        return json.dumps({
            "title": self.title,
            "company": self.company,
            "salary": self.salary,
            "experience": self.experience,
            "description": self.description,
            "link": self.link,
            "location": self.location,
            "date": self.date,
        }).encode("utf-8")


@dataclass(slots=True)
class VacanciesList:
    """A collection wrapper for VacancyEntity objects.

    Provides convenient methods for iteration, deduplication,
    and accessing vacancy metadata.
    """

    _vacancies: list[VacancyEntity] = field(default_factory=list)

    def append(self, vacancy: VacancyEntity) -> None:
        """Adds a new vacancy entity to the collection.

        Args:
            vacancy (VacancyEntity): The vacancy object to append.
        """
        self._vacancies.append(vacancy)

    @property
    def unique_hashes(self) -> list[str]:
        """Returns a list of unique vacancy hashes present in the collection.

        Useful for bulk-checking existing records in a database.

        Returns:
            list[str]: A list of unique SHA-256 hash strings.
        """
        return list({vacancy.hash for vacancy in self._vacancies})

    def __iter__(self) -> Iterator[VacancyEntity]:
        """Enables direct iteration over the collection.

        Returns:
            Iterator[VacancyEntity]: An iterator for the internal vacancy list.
        """
        return iter(self._vacancies)

    def __len__(self) -> int:
        """Returns the total number of vacancies in the list.

        Returns:
            int: Vacancy count.
        """
        return len(self._vacancies)

    def __repr__(self) -> str:
        """Returns a string representation of the VacanciesList.

        Returns:
            str: Formatted string with the list size.
        """
        return f"VacancyList(len={len(self._vacancies)})"
