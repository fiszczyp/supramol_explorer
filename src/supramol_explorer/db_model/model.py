"""Schema for the experimental results database."""

# Ignore the ORM id shadowing a Python builtin id.
# flake8: noqa: A003

from datetime import (
    datetime,
    timedelta,
)
from enum import IntEnum, StrEnum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class ReagentRole(StrEnum):
    """Reagent roles."""

    amine = "amine"
    carbonyl = "carbonyl"
    metal = "metal"


class ConfidenceEnum(IntEnum):
    """Confidence scores."""

    CERTAIN = 100
    HIGH = 75
    MEDIUM = 50
    LOW = 25
    NONE = 0


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
        Exact mass of the main component (ideally monoisotopic for future m/z
        calculations), i.e. the cation for metal sources.
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
    __mapper_args__ = {
        "polymorphic_on": "role",
        "polymorphic_identity": "reagent",
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    cas_number: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    exact_mass: Mapped[float]
    role: Mapped[ReagentRole]
    descriptors: Mapped[list["ReagentDescriptor"]] = relationship(
        back_populates="reagent"
    )

    def __repr__(self) -> str:
        return (
            "Reagent("
            f"id={self.id!r}, "
            f"cas_number={self.cas_number!r}, "
            f"name={self.name!r}, "
            f"exact_mass={self.exact_mass!r}, "
            f"role={self.role!r})"
        )


class MetalReagent(Reagent):
    __tablename__ = "metal"
    __mapper_args__ = {
        "polymorphic_identity": "metal",
    }

    id: Mapped[int] = mapped_column(ForeignKey("reagent.id"), primary_key=True)
    anion_name: Mapped[str]
    anion_exact_mass: Mapped[float]


class HasNMR:
    nmr_data: Mapped[str] = mapped_column(
        nullable=True,
        use_existing_column=True,
    )


class AmineReagent(HasNMR, Reagent):
    __tablename__ = "amine"
    __mapper_args__ = {
        "polymorphic_identity": "amine",
    }

    id: Mapped[int] = mapped_column(ForeignKey("reagent.id"), primary_key=True)


class CarbonylReagent(HasNMR, Reagent):
    __tablename__ = "carbonyl"
    __mapper_args__ = {
        "polymorphic_identity": "carbonyl",
    }

    id: Mapped[int] = mapped_column(ForeignKey("reagent.id"), primary_key=True)


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
    reagent: Mapped["Reagent"] = relationship(back_populates="descriptors")

    def __repr__(self) -> str:
        return (
            "ReagentDescriptor("
            f"reagent_id={self.reagent_id!r}, "
            f"descriptor_id={self.descriptor_id!r}, "
            f"value={self.value!r})"
        )


class NMRProcessingParameterSet(Base):
    """NMR processing parameter set."""

    __tablename__ = "nmr_processing_params"

    id: Mapped[int] = mapped_column(primary_key=True)
    relative_height: Mapped[float]
    peak_picking_range_left: Mapped[float]
    peak_picking_range_right: Mapped[float]
    peak_picking_threshold: Mapped[float]
    spectrum_size: Mapped[int]
    line_broadening: Mapped[float]


class NMRProcessedData(Base):
    """NMR processed data."""

    __tablename__ = "nmr_processed_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    nmr_proc_params_id: Mapped[int] = mapped_column(
        ForeignKey("nmr_processing_params.id")
    )
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiment.id"))

    nmr_proc_params: Mapped["NMRProcessingParameterSet"] = relationship(
        foreign_keys=[nmr_proc_params_id]
    )

    nmr_peaks: Mapped[list["NMRPeak"]] = relationship(
        back_populates="nmr_data"
    )
    experiment: Mapped["Experiment"] = relationship(back_populates="nmr_data")
    interpretations: Mapped[list["NMRInterpretation"]] = relationship(
        back_populates="nmr_data"
    )


class NMRPeak(Base):
    """NMR peak data."""

    __tablename__ = "nmr_peaks_ppm"

    id: Mapped[int] = mapped_column(primary_key=True)
    nmr_data_id: Mapped[int] = mapped_column(
        ForeignKey("nmr_processed_data.id")
    )
    peak_ppm: Mapped[float]
    is_sm: Mapped[bool]

    nmr_data: Mapped["NMRProcessedData"] = relationship(
        back_populates="nmr_peaks"
    )


class NMRDecisionParameterSet(Base):
    """Decision making set for NMR."""

    __tablename__ = "nmr_decision_params"

    id: Mapped[int] = mapped_column(primary_key=True)
    peak_number_tolerance: Mapped[int]
    peak_shift_proportion: Mapped[float]
    sm_peaks_allowed: Mapped[bool]


class NMRInterpretation(Base):
    """NMR interpretation data."""

    __tablename__ = "nmr_interpretation"

    id: Mapped[int] = mapped_column(primary_key=True)
    nmr_decision_params_id: Mapped[int] = mapped_column(
        ForeignKey("nmr_decision_params.id")
    )
    nmr_data_id: Mapped[int] = mapped_column(
        ForeignKey("nmr_processed_data.id")
    )
    symmetrical: Mapped[bool]
    pure: Mapped[bool]
    confidence: Mapped[ConfidenceEnum]

    nmr_decision_params: Mapped["NMRDecisionParameterSet"] = relationship(
        foreign_keys=[nmr_decision_params_id]
    )
    nmr_data: Mapped["NMRProcessedData"] = relationship(
        foreign_keys=[nmr_data_id],
        back_populates="interpretations",
    )


class MSProcessingParameterSet(Base):
    """MS processing parameter set."""

    __tablename__ = "ms_processing_params"

    id: Mapped[int] = mapped_column(primary_key=True)
    tic_pp_height: Mapped[float]
    tic_pp_distance: Mapped[float]
    ms_pp_height: Mapped[float]
    ms_pp_distance: Mapped[float]


class MSProcessedData(Base):
    """MS processed data."""

    __tablename__ = "ms_processed_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiment.id"))
    ms_proc_params_id: Mapped[int] = mapped_column(
        ForeignKey("ms_processing_params.id")
    )

    ms_proc_params: Mapped["MSProcessingParameterSet"] = relationship(
        foreign_keys=[ms_proc_params_id]
    )

    experiment: Mapped["Experiment"] = relationship(back_populates="ms_data")
    mz_values: Mapped[list["MZValueObserved"]] = relationship(
        back_populates="ms_data"
    )
    interpretations: Mapped[list["MSInterpretation"]] = relationship(
        back_populates="ms_data"
    )


class MZValueObserved(Base):
    """Observed m/z value data."""

    __tablename__ = "mz_observed"

    id: Mapped[int] = mapped_column(primary_key=True)
    ms_data_id: Mapped[int] = mapped_column(ForeignKey("ms_processed_data.id"))
    mz_value: Mapped[float]

    ms_data: Mapped["MSProcessedData"] = relationship(
        back_populates="mz_values"
    )
    mz_matches: Mapped[list["MZMatch"]] = relationship(
        back_populates="mz_observed"
    )


class MZValuePredicted(Base):
    """Predicted m/z value data."""

    __tablename__ = "mz_predicted"

    id: Mapped[int] = mapped_column(primary_key=True)
    assembly_id: Mapped[int] = mapped_column(ForeignKey("assembly.id"))

    n_anions: Mapped[int]
    exact_mass: Mapped[float]
    charge: Mapped[int]
    mz_value: Mapped[float]

    assembly: Mapped["SupramolecularAssembly"] = relationship(
        back_populates="mz_predictions"
    )
    mz_matches: Mapped[list["MZMatch"]] = relationship(
        back_populates="mz_predicted"
    )


class MZTolerance(Base):
    """Tolerance for m/z values."""

    __tablename__ = "mz_tolerance"

    id: Mapped[int] = mapped_column(primary_key=True)
    atol: Mapped[float]


class MZMatch(Base):
    """Matches between m/z values within tolerance."""

    __tablename__ = "mz_match"

    mz_observed_id: Mapped[int] = mapped_column(
        ForeignKey("mz_observed.id"), primary_key=True
    )
    mz_predicted_id: Mapped[int] = mapped_column(
        ForeignKey("mz_predicted.id"), primary_key=True
    )
    mz_tolerance_id: Mapped[int] = mapped_column(
        ForeignKey("mz_tolerance.id"), primary_key=True
    )

    mz_observed: Mapped["MZValueObserved"] = relationship(
        back_populates="mz_matches"
    )
    mz_predicted: Mapped["MZValuePredicted"] = relationship(
        back_populates="mz_matches"
    )
    mz_tolerance: Mapped["MZTolerance"] = relationship(
        foreign_keys=[mz_tolerance_id]
    )


class MSDecisionParameterSet(Base):
    """Decision making set for MS."""

    __tablename__ = "ms_decision_params"

    id: Mapped[int] = mapped_column(primary_key=True)
    multiple_mz_trigger_charge: Mapped[int | None]
    mz_matches_low: Mapped[int]
    mz_matches_medium: Mapped[int]
    mz_matches_high: Mapped[int]
    mz_matches_certain: Mapped[int]


class MSInterpretation(Base):
    """MS interpretation data."""

    __tablename__ = "ms_interpretation"

    id: Mapped[int] = mapped_column(primary_key=True)
    ms_decision_params_id: Mapped[int] = mapped_column(
        ForeignKey("ms_decision_params.id")
    )
    ms_data_id: Mapped[int] = mapped_column(ForeignKey("ms_processed_data.id"))
    assembly_id: Mapped[int] = mapped_column(ForeignKey("assembly.id"))
    confidence: Mapped[ConfidenceEnum]

    ms_decision_params: Mapped["MSDecisionParameterSet"] = relationship(
        foreign_keys=[ms_decision_params_id]
    )
    ms_data: Mapped["MSProcessedData"] = relationship(
        foreign_keys=[ms_data_id],
        back_populates="interpretations",
    )
    assembly: Mapped["SupramolecularAssembly"] = relationship(
        foreign_keys=[assembly_id],
        back_populates="interpretations",
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
    nmr_data_path: Mapped[str]
    ms_data_path: Mapped[str]

    amine_id: Mapped[int] = mapped_column(ForeignKey("reagent.id"))
    carbonyl_id: Mapped[int] = mapped_column(ForeignKey("reagent.id"))
    metal_id: Mapped[int] = mapped_column(ForeignKey("reagent.id"))

    carbonyl: Mapped["Reagent"] = relationship(foreign_keys=[carbonyl_id])
    metal: Mapped["Reagent"] = relationship(foreign_keys=[metal_id])
    amine: Mapped["Reagent"] = relationship(foreign_keys=[amine_id])
    assemblies: Mapped[list["SupramolecularAssembly"] | None] = relationship(
        back_populates="experiment"
    )
    ms_data: Mapped[list["MSProcessedData"]] = relationship(
        back_populates="experiment"
    )
    nmr_data: Mapped[list["NMRProcessedData"]] = relationship(
        back_populates="experiment"
    )

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


class SupramolecularAssembly(Base):
    """Possible supramolecular assemblies."""

    __tablename__ = "assembly"

    id: Mapped[int] = mapped_column(primary_key=True)
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiment.id"))
    topology_id: Mapped[int] = mapped_column(ForeignKey("topology.id"))
    cation_exact_mass: Mapped[float]

    experiment: Mapped["Experiment"] = relationship(
        back_populates="assemblies"
    )
    topology: Mapped["AssemblyTopology"] = relationship(
        foreign_keys=[topology_id]
    )
    mz_predictions: Mapped[list["MZValuePredicted"]] = relationship(
        back_populates="assembly"
    )
    interpretations: Mapped[list["MSInterpretation"]] = relationship(
        back_populates="assembly"
    )


class AssemblyTopology(Base):
    """Possible topologies of the supramolecular assemblies."""

    __tablename__ = "topology"

    id: Mapped[int] = mapped_column(primary_key=True)

    n_metals: Mapped[int]
    n_amines: Mapped[int]
    n_carbonyls: Mapped[int]

    amine_topicity: Mapped[int]
    carbonyl_topicity: Mapped[int]
    coordination_number: Mapped[int]
