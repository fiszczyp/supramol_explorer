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

    def __repr__(self) -> str:
        return f"ReagentRole.{self.name}"


class ConfidenceEnum(IntEnum):
    """Confidence scores."""

    CERTAIN = 100
    HIGH = 75
    MEDIUM = 50
    LOW = 25
    NONE = 0

    def __repr__(self) -> str:
        return f"ConfidenceEnum.{self.name}"


class Base(DeclarativeBase):
    """Declarative ORM base class for SQLAlchemy."""

    pass


class Reagent(Base):
    """Data related to all the reagents used in the workflow.

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

    Notes
    -----
    This is a base reagent class from which more specific reagent classes might
    inherit (e.g., if they are allowed to store additional data).

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
            f"cas_number={self.cas_number!r}, "
            f"name={self.name!r}, "
            f"exact_mass={self.exact_mass!r}, "
            f"role={self.role!r})"
        )


class MetalReagent(Reagent):
    """Data related to metal reagents.

    Extends the Reagent class by data fields relevant to metals used in the
    workflow, such as the anion information.

    Attributes
    ----------
    anion_name
        Name of the anion.
    anion_exact_mass
        Exact mass of the anion, ideally monoisotopic for m/z calculations.

    """

    __tablename__ = "metal"
    __mapper_args__ = {
        "polymorphic_identity": "metal",
    }

    id: Mapped[int] = mapped_column(ForeignKey("reagent.id"), primary_key=True)
    anion_name: Mapped[str]
    anion_exact_mass: Mapped[float]

    def __repr__(self) -> str:
        return (
            "MetalReagent("
            f"cas_number={self.cas_number!r}, "
            f"name={self.name!r}, "
            f"exact_mass={self.exact_mass!r}, "
            f"role={self.role!r}, "
            f"anion_name={self.anion_name!r}, "
            f"anion_exact_mass={self.anion_exact_mass!r})"
        )


class _HasNMR:
    """Mixin class for reagents that contain NMR data.

    Attributes
    ----------
    nmr_data
        Path to the NMR data folder.

    """

    nmr_data: Mapped[str] = mapped_column(
        nullable=True,
        use_existing_column=True,
    )


class AmineReagent(_HasNMR, Reagent):
    """Data related to amine reagents.

    Notes
    -----
    Extends the Reagent class with a NMR data through the HasNMR mixin.

    """

    __tablename__ = "amine"
    __mapper_args__ = {
        "polymorphic_identity": "amine",
    }

    id: Mapped[int] = mapped_column(ForeignKey("reagent.id"), primary_key=True)

    def __repr__(self) -> str:
        return (
            "AmineReagent("
            f"cas_number={self.cas_number!r}, "
            f"name={self.name!r}, "
            f"exact_mass={self.exact_mass!r}, "
            f"role={self.role!r}, "
            f"nmr_data={self.nmr_data!r})"
        )


class CarbonylReagent(_HasNMR, Reagent):
    """Data related to amine reagents.

    Notes
    -----
    Extends the Reagent class with a NMR data through the HasNMR mixin.

    """

    __tablename__ = "carbonyl"
    __mapper_args__ = {
        "polymorphic_identity": "carbonyl",
    }

    id: Mapped[int] = mapped_column(ForeignKey("reagent.id"), primary_key=True)

    def __repr__(self) -> str:
        return (
            "CarbonylReagent("
            f"cas_number={self.cas_number!r}, "
            f"name={self.name!r}, "
            f"exact_mass={self.exact_mass!r}, "
            f"role={self.role!r}, "
            f"nmr_data={self.nmr_data!r})"
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
        return f"Descriptor(name={self.name!r})"


class ReagentDescriptor(Base):
    """
    Association of reagents with their cheminformatics descriptors.

    Attributes
    ----------
    reagent
        A reagent that the value corresponds to.
    descriptor
        A descriptor whose value is stored.
    value
        Value of the descriptor, parsing has to be handled separately.

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
            f"reagent={self.reagent!r}, "
            f"descriptor={self.descriptor!r}, "
            f"value={self.value!r})"
        )


class NMRProcessingParameterSet(Base):
    """Parameters set for NMR data processing.

    Attributes
    ----------
    relative_height
        Relative peak height used for peak picking.
    peak_picking_threshold
        Peak threshold used for peak picking.
    peak_picking_range_left
        Downfield limit of the peak picking range (in ppm).
    peak_picking_range_right
        Upfield limit of the peak picking range (in ppm).
    spectrum_size
        Size of the spectrum (used for zero filling in TopSpin).
    line_broadening
        Exponential multiplication line broadening factor.

    """

    __tablename__ = "nmr_processing_params"

    id: Mapped[int] = mapped_column(primary_key=True)
    relative_height: Mapped[float]
    peak_picking_threshold: Mapped[float]
    peak_picking_range_left: Mapped[float]
    peak_picking_range_right: Mapped[float]
    spectrum_size: Mapped[int]
    line_broadening: Mapped[float]

    def __repr__(self) -> str:
        return (
            "NMRProcessingParameterSet("
            f"relative_height={self.relative_height!r}, "
            f"peak_picking_threshold={self.peak_picking_threshold!r}, "
            f"peak_picking_range_left={self.peak_picking_range_left!r}, "
            f"peak_picking_range_right={self.peak_picking_range_right!r}, "
            f"spectrum_size={self.spectrum_size!r}, "
            f"line_broadening={self.line_broadening!r}) "
        )


class NMRProcessedData(Base):
    """Processed NMR data.

    Attributes
    ----------
    experiment
        Experiment that the NMR data correspond to.
    nmr_proc_params
        Processing parameters that the data were processed with.

    Derived attributes
    ------------------
    nmr_peaks
        A list of NMR peaks identified in the dataset.
    interpretations
        A list of possible data interpretations of the dataset.

    """

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

    def __repr__(self) -> str:
        return (
            "NMRProcessedData("
            f"experiment={self.experiment!r}, "
            f"nmr_proc_params={self.nmr_proc_params!r}, "
            f"nmr_peaks={self.nmr_peaks!r}, "
            f"interpretations={self.interpretations!r})"
        )


class NMRPeak(Base):
    """Data related to NMR peaks.

    Attributes
    ----------
    peak_ppm
        Chemical shift of the peak.
    is_sm
        If True, the peak is assumed to originate from the starting material.
    nmr_data
        The processed NMR data object that the peak is identified in.

    """

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

    def __repr__(self) -> str:
        return (
            "NMRPeak("
            f"peak_ppm={self.peak_ppm!r}, "
            f"is_sm={self.is_sm!r}, "
            f"nmr_data={self.nmr_data!r})"
        )


class NMRDecisionParameterSet(Base):
    """Parameters set for NMR-based decisions.

    Attributes
    ----------
    peak_number_tolerance
        Difference in the number of peaks allowed from the starting materials.
    peak_shift_proportion
        A proportion of peaks that must have different chemical shifts than in
        the starting materials.
    sm_peaks_allowed
        If True, starting materials peaks will be allowed to be present in the
        NMR spectrum (might still give lower confidence ratings).

    """

    __tablename__ = "nmr_decision_params"

    id: Mapped[int] = mapped_column(primary_key=True)
    peak_number_tolerance: Mapped[int]
    peak_shift_proportion: Mapped[float]
    sm_peaks_allowed: Mapped[bool]

    def __repr__(self) -> str:
        return (
            "NMRDecisionParameterSet("
            f"peak_number_tolerance={self.peak_number_tolerance!r}, "
            f"peak_shift_proportion={self.peak_shift_proportion!r}, "
            f"sm_peaks_allowed={self.sm_peaks_allowed!r})"
        )


class NMRInterpretation(Base):
    """Interpretations of the processed NMR datasets.

    Attributes
    ----------
    nmr_data
        The processed NMR dataset that the decision is based on.
    nmr_decision_params
        Parameters upon which the decision is based.
    symmetrical
        If True, the structure is considered symmetrical.
    pure
        If True, the structure is considered pure (e.g., without starting
        materials present).
    confidence
        Algorithmic confidence in the decision made.

    """

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

    def __repr__(self) -> str:
        return (
            "NMRInterpretation("
            f"nmr_data={self.nmr_data!r}, "
            f"nmr_decision_params={self.nmr_decision_params!r}, "
            f"symmetrical={self.symmetrical!r}, "
            f"pure={self.pure!r}, "
            f"confidence={self.confidence!r})"
        )


class MSProcessingParameterSet(Base):
    """Parameters set for MS data processing.

    Attributes
    ----------
    tic_pp_height
        Relative height of the peaks used for peak picking in the total ion
        chromatogram.
    tic_pp_distance
        Peak distance used for peak picking in the total ion chromatogram.
    ms_pp_height
        Relative height of the peaks used for peak picking in the extracted
        mass spectra.
    ms_pp_distance
        Peak distance used for peak picking in the extracted mass spectra.

    """

    __tablename__ = "ms_processing_params"

    id: Mapped[int] = mapped_column(primary_key=True)
    tic_pp_height: Mapped[float]
    tic_pp_distance: Mapped[float]
    ms_pp_height: Mapped[float]
    ms_pp_distance: Mapped[float]

    def __repr__(self) -> str:
        return (
            "MSProcessingParameterSet("
            f"tic_pp_height={self.tic_pp_height!r}, "
            f"tic_pp_distance={self.tic_pp_distance!r}, "
            f"ms_pp_height={self.ms_pp_height!r}, "
            f"ms_pp_distance={self.ms_pp_distance!r})"
        )


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
