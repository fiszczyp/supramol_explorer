"""Schema for the experimental results database."""

# Ignore the ORM id shadowing a Python builtin id.
# flake8: noqa: A003

from datetime import (
    datetime,
    timedelta,
)
from enum import StrEnum
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class ReagentRole(StrEnum):
    """Reagent roles."""

    SOLVENT = "SOLVENT"
    AMINE = "AMINE"
    CARBONYL = "CARBONYL"
    METAL = "METAL"


class Base(DeclarativeBase):
    """Declarative ORM base class for SQLAlchemy."""

    pass


class Reagent(Base):
    """
    Data related to the reagents used in the workflow.

    Attributes
    ----------
    cas_number
        The unique CAS number associated with the substance.
    name
        Chemical name (either IUPAC or a nickname).
    exact_mass
        Exact mass of the molecule (ideally monoisotopic for
        future m/z calculations).
    nmr_data
        A path to the NMR data folder.
    role
        Role of the reagent in the synthesis.

    Derived attributes
    ------------------
    descriptors
        A list of the cheminformatics descriptors associated with the reagent.

    """

    __tablename__ = "reagent"

    id: Mapped[int] = mapped_column(primary_key=True)
    cas_number: Mapped[str]
    name: Mapped[str]
    exact_mass: Mapped[float]
    nmr_data: Mapped[str]
    role: Mapped[ReagentRole]
    descriptors: Mapped[List["ReagentDescriptor"]] = relationship()

    def __repr__(self) -> str:
        return (
            "Reagent("
            f"id={self.id!r}, "
            f"cas_number={self.cas_number!r}, "
            f"name={self.name!r}, "
            f"exact_mass={self.exact_mass!r}, "
            f"nmr_data={self.nmr_data!r}, "
            f"role={self.role!r})"
        )


class Descriptor(Base):
    """
    Data related to the cheminformatics descriptors.

    Attributes
    ----------
    name
        Descriptor name.

    """

    __tablename__ = "descriptor"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    def __repr__(self) -> str:
        return f"Descriptor(id={self.id!r}, name={self.name!r})"


class ReagentDescriptor(Base):
    """
    Association of reagents with their cheminformatics descriptors.

    Attributes
    ----------
    reagent_id
        Unique ID of the reagent.
    descriptor_id
        Unique ID of the descriptor.
    value
        Value of the descriptor, parsing has to be handled separately.

    Derived attributes
    ------------------
    descriptor
        A relationship to the corresponding descriptor object.

    """

    __tablename__ = "reagent_descriptor"

    reagent_id: Mapped[int] = mapped_column(
        ForeignKey("reagent.id"), primary_key=True
    )
    descriptor_id: Mapped[int] = mapped_column(
        ForeignKey("descriptor.id"), primary_key=True
    )
    value: Mapped[str]
    descriptor: Mapped["Descriptor"] = relationship()

    def __repr__(self) -> str:
        return (
            "ReagentDescriptor("
            f"reagent_id={self.reagent_id!r}, "
            f"descriptor_id={self.descriptor_id!r}, "
            f"value={self.value!r})"
        )


class Experiment(Base):
    """
    Class collating all the data related to each experiment.

    Attributes
    ----------
    date
        Experiment date.
    solvent
        Reaction solvent.
    temperature
        Reaction temperature (in K).
    time
        Reaction time.
    nmr_data
        A path to the NMR data folder.
    ms_data
        A path to the MS data folder.
    amine_id
        Unique ID of the amine.
    carbonyl_id
        Unique ID of the carbonyl.
    metal_id
        Unique ID of the metal.

    Derived attributes
    ------------------
    amine
        Reagent object corresponding to the amine.
    carbonyl
        Reagent object corresponding to the carbonyl.
    metal
        Reagent object corresponding to the metal.

    """

    __tablename__ = "experiment"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime]
    solvent: Mapped[str]
    temperature: Mapped[float]
    time: Mapped[timedelta]
    nmr_data: Mapped[str]
    ms_data: Mapped[str]

    amine_id: Mapped[int] = mapped_column(ForeignKey("reagent.id"))
    carbonyl_id: Mapped[int] = mapped_column(ForeignKey("reagent.id"))
    metal_id: Mapped[int] = mapped_column(ForeignKey("reagent.id"))

    amine: Mapped["Reagent"] = relationship(foreign_keys=[amine_id])
    carbonyl: Mapped["Reagent"] = relationship(foreign_keys=[carbonyl_id])
    metal: Mapped["Reagent"] = relationship(foreign_keys=[metal_id])

    def __repr__(self) -> str:
        return (
            "Experiment("
            f"id={self.id!r}, "
            f"date={self.date!r}, "
            f"solvent={self.solvent!r}, "
            f"temperature={self.temperature!r}, "
            f"time={self.time!r}, "
            f"nmr_data={self.nmr_data!r}, "
            f"ms_data={self.ms_data!r}, "
            f"amine_id={self.amine_id!r}, "
            f"carbonyl_id={self.carbonyl_id!r}, "
            f"metal_id={self.metal_id!r})"
        )
