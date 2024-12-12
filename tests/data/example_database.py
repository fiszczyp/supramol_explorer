"""
Simple database with entries for all tables.

!TODO!: Convert into fixtures in the future?

"""

from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from supramol_explorer.db_model.model import (
    AmineReagent,
    AssemblyTopology,
    Base,
    CarbonylReagent,
    ConfidenceEnum,
    Descriptor,
    Experiment,
    Ion,
    MetalReagent,
    MSDecisionParameterSet,
    MSInterpretation,
    MSProcessedData,
    MSProcessingParameterSet,
    MZMatch,
    MZTolerance,
    MZValueObserved,
    MZValuePredicted,
    NMRDecisionParameterSet,
    NMRInterpretation,
    NMRPeak,
    NMRProcessedData,
    NMRProcessingParameterSet,
    ReagentDescriptor,
    ReagentRole,
    SupramolecularAssembly,
)

engine = create_engine("sqlite://")
Base.metadata.create_all(engine)

Session = sessionmaker(engine)

############################################
##### REAGENTS AND DESCRIPTORS #############
############################################

# Create a metal with two descriptors

zinc = Ion(name="Zn(II)", charge=2, formula="[Zn+2]", exact_mass=63.9)
triflate = Ion(name="OTf", charge=-1, formula="SO3CF3-", exact_mass=149.0)

metal = MetalReagent(
    name="Zinc triflate",
    exact_mass="1000",
    role=ReagentRole.metal,
    cation=zinc,
    num_cations=1,
    anion=triflate,
    num_anions=2,
)

metal.descriptors.extend(
    [
        ReagentDescriptor(descriptor=Descriptor(name="radius"), value="0.88"),
        ReagentDescriptor(descriptor=Descriptor(name="charge"), value="2"),
    ]
)

# Create an amine with no descriptors

amine = AmineReagent(
    cas_number="108-72-5",
    name="ethylenediamine",
    exact_mass=123.2,
    nmr_data="tests/data/nmr/amine",
    role=ReagentRole.amine,
)

# Create two carbonyl with one descriptor

carbonyl_distance = Descriptor(name="distance")

carbonyl1 = CarbonylReagent(
    cas_number="872-85-5",
    name="4-pyridinecarboxaldehyde",
    exact_mass=107.1,
    nmr_data="tests/data/nmr/p-aldehyde",
    role=ReagentRole.carbonyl,
)

carbonyl1.descriptors.append(
    ReagentDescriptor(descriptor=carbonyl_distance, value="3"),
)

carbonyl2 = CarbonylReagent(
    cas_number="1121-60-4",
    name="2-pyridinecarboxaldehyde",
    exact_mass=107.1,
    nmr_data="tests/data/nmr/o-aldehyde",
    role=ReagentRole.carbonyl,
)

carbonyl2.descriptors.append(
    ReagentDescriptor(descriptor=carbonyl_distance, value="1"),
)

# Add all reagents into the database

with Session() as session:
    session.add_all([metal, amine, carbonyl1, carbonyl2])

    try:
        session.commit()
    except IntegrityError:
        session.rollback()


############################################
########## EXPERIMENTS: FAILED #############
############################################


failed_experiment = Experiment(
    date=datetime(year=2024, month=10, day=29),
    solvent="acetonitrile",
    temperature=363,
    time=timedelta(hours=18),
    nmr_data_path="tests/data/nmr/reaction1",
    ms_data_path="tests/data/ms/reaction1",
    amine=amine,
    carbonyl=carbonyl1,
    metal=metal,
)

cage_topology = AssemblyTopology(
    n_metals=4,
    n_amines=4,
    n_carbonyls=12,
    amine_topicity=3,
    carbonyl_topicity=1,
    coordination_number=6,
)

cage_assembly_failed = SupramolecularAssembly(
    experiment=failed_experiment,
    topology=cage_topology,
    cation_exact_mass=1817.6,
)

############################################
########## POSSIBLE MZ VALUES ##############
############################################

cage_8 = MZValuePredicted(
    assembly=cage_assembly_failed,
    n_anions=0,
    exact_mass=1817.6,
    charge=8,
    mz_value=227.2,
)

cage_6 = MZValuePredicted(
    assembly=cage_assembly_failed,
    n_anions=2,
    exact_mass=1945.4,
    charge=6,
    mz_value=324.2,
)

cage_4 = MZValuePredicted(
    assembly=cage_assembly_failed,
    n_anions=4,
    exact_mass=2073.2,
    charge=4,
    mz_value=518.3,
)

cage_assembly_failed.mz_predictions.extend(
    [
        cage_4,
        cage_6,
        cage_8,
    ]
)


with Session() as session:
    session.add_all(
        [
            failed_experiment,
            cage_assembly_failed,
            cage_8,
            cage_6,
            cage_4,
        ]
    )

    try:
        session.commit()
    except IntegrityError:
        session.rollback()

############################################
########## EXPERIMENTS: PASSED #############
############################################

passed_experiment = Experiment(
    date=datetime(year=2024, month=10, day=30),
    solvent="acetonitrile",
    temperature=363,
    time=timedelta(hours=18),
    nmr_data_path="tests/data/nmr/reaction2",
    ms_data_path="tests/data/ms/reaction2",
    amine=amine,
    carbonyl=carbonyl2,
    metal=metal,
)

cage_assembly_passed = SupramolecularAssembly(
    experiment=passed_experiment,
    topology=cage_topology,
    cation_exact_mass=1817.6,
)

############################################
########## POSSIBLE MZ VALUES ##############
############################################

cage_8 = MZValuePredicted(
    assembly=cage_assembly_passed,
    n_anions=0,
    exact_mass=1817.6,
    charge=8,
    mz_value=227.2,
)

cage_6 = MZValuePredicted(
    assembly=cage_assembly_passed,
    n_anions=2,
    exact_mass=1945.4,
    charge=6,
    mz_value=324.2,
)

cage_4 = MZValuePredicted(
    assembly=cage_assembly_passed,
    n_anions=4,
    exact_mass=2073.2,
    charge=4,
    mz_value=518.3,
)

cage_assembly_passed.mz_predictions.extend(
    [
        cage_4,
        cage_6,
        cage_8,
    ]
)


with Session() as session:
    session.add_all(
        [
            passed_experiment,
            cage_assembly_passed,
            cage_8,
            cage_6,
            cage_4,
        ]
    )

    try:
        session.commit()
    except IntegrityError:
        session.rollback()

############################################
########## "EXPERIMENTAL" DATA 1 ###########
############################################

nmr_params_high = NMRProcessingParameterSet(
    relative_height=150,
    peak_picking_range_left=12,
    peak_picking_range_right=5,
    peak_picking_threshold=25,
    spectrum_size=16000,
    line_broadening=1.2,
)

nmr_params_low = NMRProcessingParameterSet(
    relative_height=150,
    peak_picking_range_left=12,
    peak_picking_range_right=5,
    peak_picking_threshold=1,
    spectrum_size=16000,
    line_broadening=1.2,
)

nmr_data1_high = NMRProcessedData(
    experiment=failed_experiment,
    nmr_proc_params=nmr_params_high,
)

nmr_data1_low = NMRProcessedData(
    experiment=failed_experiment,
    nmr_proc_params=nmr_params_low,
)

nmr_data1_high_peaks = [
    NMRPeak(peak_ppm=11, is_sm=True),
    NMRPeak(peak_ppm=8, is_sm=True),
    NMRPeak(peak_ppm=7, is_sm=True),
]

nmr_data1_low_peaks = [
    NMRPeak(peak_ppm=11, is_sm=True),
    NMRPeak(peak_ppm=8, is_sm=True),
    NMRPeak(peak_ppm=7, is_sm=True),
    NMRPeak(peak_ppm=6, is_sm=False),
]

nmr_data1_high.nmr_peaks.extend(nmr_data1_high_peaks)
nmr_data1_low.nmr_peaks.extend(nmr_data1_low_peaks)

nmr_decision_params_sm = NMRDecisionParameterSet(
    peak_number_tolerance=2,
    peak_shift_proportion=0.5,
    sm_peaks_allowed=True,
)

nmr_decision_params_nosm = NMRDecisionParameterSet(
    peak_number_tolerance=2,
    peak_shift_proportion=0.5,
    sm_peaks_allowed=False,
)

nmr_interpretation_high_sm = NMRInterpretation(
    nmr_decision_params=nmr_decision_params_sm,
    nmr_data=nmr_data1_high,
    symmetrical=False,
    pure=False,
    confidence=ConfidenceEnum.NONE,
)

nmr_interpretation_high_nosm = NMRInterpretation(
    nmr_decision_params=nmr_decision_params_nosm,
    nmr_data=nmr_data1_high,
    symmetrical=False,
    pure=False,
    confidence=ConfidenceEnum.NONE,
)

nmr_interpretation_low_sm = NMRInterpretation(
    nmr_decision_params=nmr_decision_params_sm,
    nmr_data=nmr_data1_low,
    symmetrical=False,
    pure=False,
    confidence=ConfidenceEnum.NONE,
)

nmr_interpretation_low_nosm = NMRInterpretation(
    nmr_decision_params=nmr_decision_params_nosm,
    nmr_data=nmr_data1_low,
    symmetrical=False,
    pure=False,
    confidence=ConfidenceEnum.LOW,
)

ms_processing_params = MSProcessingParameterSet(
    tic_pp_height=20,
    tic_pp_distance=5,
    ms_pp_height=20,
    ms_pp_distance=10,
)

ms_decision_params = MSDecisionParameterSet(
    multiple_mz_trigger_charge=3,
    mz_matches_low=1,
    mz_matches_medium=2,
    mz_matches_high=3,
    mz_matches_certain=4,
)

ms_decision_params_any = MSDecisionParameterSet(
    multiple_mz_trigger_charge=None,
    mz_matches_low=1,
    mz_matches_medium=1,
    mz_matches_high=1,
    mz_matches_certain=1,
)

ms_data1 = MSProcessedData(
    experiment=failed_experiment,
    ms_proc_params=ms_processing_params,
)

ms_data1.interpretations.append(
    MSInterpretation(
        confidence=ConfidenceEnum.NONE,
        ms_decision_params=ms_decision_params,
        assembly=cage_assembly_failed,
    )
)

with Session() as session:
    session.add_all(
        [
            nmr_params_high,
            nmr_params_low,
            nmr_data1_high,
            nmr_data1_low,
            nmr_interpretation_high_nosm,
            nmr_interpretation_high_sm,
            nmr_interpretation_low_nosm,
            nmr_interpretation_low_sm,
            ms_data1,
        ]
    )

    try:
        session.commit()
    except IntegrityError:
        session.rollback()

############################################
########## "EXPERIMENTAL" DATA 2 ###########
############################################

nmr_data2_high = NMRProcessedData(
    experiment=passed_experiment,
    nmr_proc_params=nmr_params_high,
    nmr_peaks=[
        NMRPeak(peak_ppm=8.5, is_sm=False),
        NMRPeak(peak_ppm=6, is_sm=False),
    ],
)

nmr_data2_low = NMRProcessedData(
    experiment=passed_experiment,
    nmr_proc_params=nmr_params_low,
    nmr_peaks=[
        NMRPeak(peak_ppm=11, is_sm=True),
        NMRPeak(peak_ppm=8.5, is_sm=False),
        NMRPeak(peak_ppm=8, is_sm=True),
        NMRPeak(peak_ppm=7, is_sm=True),
        NMRPeak(peak_ppm=6, is_sm=False),
    ],
)

nmr_interpretation_high_sm = NMRInterpretation(
    nmr_decision_params=nmr_decision_params_sm,
    nmr_data=nmr_data2_high,
    symmetrical=True,
    pure=True,
    confidence=ConfidenceEnum.CERTAIN,
)

nmr_interpretation_high_nosm = NMRInterpretation(
    nmr_decision_params=nmr_decision_params_nosm,
    nmr_data=nmr_data2_high,
    symmetrical=True,
    pure=True,
    confidence=ConfidenceEnum.CERTAIN,
)

nmr_interpretation_low_sm = NMRInterpretation(
    nmr_decision_params=nmr_decision_params_sm,
    nmr_data=nmr_data2_low,
    symmetrical=True,
    pure=False,
    confidence=ConfidenceEnum.CERTAIN,
)

nmr_interpretation_low_nosm = NMRInterpretation(
    nmr_decision_params=nmr_decision_params_nosm,
    nmr_data=nmr_data2_low,
    symmetrical=True,
    pure=False,
    confidence=ConfidenceEnum.MEDIUM,
)

ms_data2 = MSProcessedData(
    experiment=passed_experiment,
    ms_proc_params=ms_processing_params,
)

ms_peaks = [
    MZValueObserved(
        ms_data=ms_data2,
        mz_value=227.1,
    ),
    MZValueObserved(
        ms_data=ms_data2,
        mz_value=324.3,
    ),
    MZValueObserved(
        ms_data=ms_data2,
        mz_value=518.35,
    ),
]

mz_atol = MZTolerance(atol=0.2)

matches = [
    MZMatch(
        mz_observed=ms_peaks[0], mz_predicted=cage_8, mz_tolerance=mz_atol
    ),
    MZMatch(
        mz_observed=ms_peaks[1], mz_predicted=cage_6, mz_tolerance=mz_atol
    ),
    MZMatch(
        mz_observed=ms_peaks[2], mz_predicted=cage_4, mz_tolerance=mz_atol
    ),
]

ms_data2.mz_values.extend(ms_peaks)

ms_data2.interpretations.extend(
    [
        MSInterpretation(
            confidence=ConfidenceEnum.HIGH,
            ms_decision_params=ms_decision_params,
            assembly=cage_assembly_passed,
        ),
        MSInterpretation(
            confidence=ConfidenceEnum.CERTAIN,
            ms_decision_params=ms_decision_params_any,
            assembly=cage_assembly_passed,
        ),
    ]
)

with Session() as session:
    session.add_all(
        [
            nmr_data2_high,
            nmr_data2_low,
            nmr_interpretation_high_nosm,
            nmr_interpretation_high_sm,
            nmr_interpretation_low_nosm,
            nmr_interpretation_low_sm,
            ms_data2,
        ]
    )

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
