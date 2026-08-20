import numpy as np
import MDAnalysis as mda
from MDAnalysis.analysis import align, rms
from MDAnalysis.transformations import center_in_box
from MDAnalysis.transformations.nojump import NoJump
import barnaba as bb

# =========================================================
# Input files
# =========================================================
PSF = "step3_charmm2omm.psf"
DCD = "./tmp/step5_all_2us.dcd"
REFPDB = "step3_charmm2omm.pdb"

# =========================================================
# Load systems
# =========================================================
u = mda.Universe(PSF, DCD)
ref = mda.Universe(PSF, REFPDB)

print("Loaded trajectory")
print("Number of frames: {}".format(len(u.trajectory)))

# =========================================================
# Atom selections
# =========================================================
dna = u.select_atoms("(segid DNAA DNAB) and nucleic")

sel = (
    "(segid DNAA DNAB) and nucleic "
    "and not name H* "
    "and not name D*"
)

ref_sel = ref.select_atoms(sel)

print("Selected atoms: {}".format(len(dna)))
print("Alignment atoms: {}".format(len(ref_sel)))

# =========================================================
# PBC correction + centering
# =========================================================
print("Applying NoJump and centering transformations")

u.trajectory.add_transformations(
    NoJump(dna),
    center_in_box(dna)
)

# =========================================================
# Align trajectory
# =========================================================
print("Aligning trajectory")

aligner = align.AlignTraj(
    u,
    ref,
    select=sel,
    in_memory=False
)

aligner.run()

print("Alignment complete")

# =========================================================
# RMSD
# =========================================================
print("Calculating RMSD")

R = rms.RMSD(
    u.select_atoms(sel),
    ref_sel,
    center=False,
    superposition=False
).run()

rmsd_out = R.results.rmsd

np.savetxt(
    "rmsd_DNA_noH_noDrude.dat",
    rmsd_out,
    header="frame time_ps rmsd_A",
    fmt="%.6f"
)

print("Wrote rmsd_DNA_noH_noDrude.dat")

# =========================================================
# Write DNA-only reference PDB
# =========================================================
dna_ref = ref.select_atoms(
    "(segid DNAA DNAB) and nucleic"
)

dna_ref.write("ref_dna_only.pdb")

print("Wrote ref_dna_only.pdb")

# =========================================================
# Write aligned DNA-only trajectory
# =========================================================
print("Writing aligned DNA-only trajectory")

with mda.Writer(
    "aligned_dna.dcd",
    dna.n_atoms
) as W:

    for ts in u.trajectory:
        W.write(dna)

print("Wrote aligned_dna.dcd")

# =========================================================
# eRMSD with Barnaba
# =========================================================
print("Calculating eRMSD")

ermsd_values = bb.ermsd(
    "ref_dna_only.pdb",
    "aligned_dna.dcd",
    topology="ref_dna_only.pdb"
)

ermsd_values = np.array(ermsd_values)

# =========================================================
# Combine RMSD + eRMSD
# =========================================================
frames = rmsd_out[:, 0]
times = rmsd_out[:, 1]
rmsd_vals = rmsd_out[:, 2]

n = min(
    len(frames),
    len(ermsd_values)
)

out = np.column_stack([
    frames[:n],
    times[:n],
    rmsd_vals[:n],
    ermsd_values[:n]
])

np.savetxt(
    "rmsd_ermsd_DNA.dat",
    out,
    header="frame time_ps rmsd_A eRMSD",
    fmt="%.6f"
)

print("Wrote rmsd_ermsd_DNA.dat")

# =========================================================
# Statistics
# =========================================================
print("")
print("===== Statistics =====")

print(
    "Frames: {}".format(
        len(ermsd_values)
    )
)

print(
    "eRMSD mean: {:.4f}".format(
        np.mean(ermsd_values)
    )
)

print(
    "eRMSD std: {:.4f}".format(
        np.std(ermsd_values)
    )
)

print(
    "eRMSD < 0.7 (near-native): {} frames".format(
        np.sum(ermsd_values < 0.7)
    )
)

print(
    "Fraction near-native: {:.3f}".format(
        np.sum(ermsd_values < 0.7) /
        float(len(ermsd_values))
    )
)
