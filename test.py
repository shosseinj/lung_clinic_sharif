import SimpleITK as sitk, numpy as np, matplotlib.pyplot as plt, os, glob

# ---------- 1.  load any pair -------------------------------------------------
def load_dicoms(folder):
    files = sorted(glob.glob(os.path.join(folder, '*')))
    reader = sitk.ImageSeriesReader()
    reader.SetFileNames(reader.GetGDCMSeriesFileNames(folder))
    img = reader.Execute()
    return sitk.Cast(img, sitk.sitkFloat32)

exhale = load_dicoms('./data/SR_3')   # << your folders
inhale = load_dicoms('./data/SR_2')

# ---------- 2.  32 mm Y translation ------------------------------------------
shift_mm = np.array([0., 32., 0.])
print('shift (mm):', shift_mm)

t = sitk.TranslationTransform(3)
t.SetOffset(shift_mm.tolist())

inhale_shifted = sitk.Resample(inhale, exhale, t, sitk.sitkLinear, -1000.)

# ---------- 3.  quick overlay -------------------------------------------------
z = exhale.GetSize()[2] // 2
ex_sl  = sitk.GetArrayFromImage(exhale)[z]
mv_sl  = sitk.GetArrayFromImage(inhale_shifted)[z]

plt.figure(figsize=(15,5))
plt.subplot(131); plt.imshow(ex_sl, cmap='gray', vmin=-1000, vmax=200); plt.title('exhale'); plt.axis('off')
plt.subplot(132); plt.imshow(mv_sl, cmap='gray', vmin=-1000, vmax=200); plt.title('inhale shifted'); plt.axis('off')
plt.subplot(133)
plt.imshow(ex_sl, cmap='gray', vmin=-1000, vmax=200)
plt.imshow(mv_sl, cmap='hot', alpha=0.5)
plt.title('overlay'); plt.axis('off')
plt.savefig('shift32_test.png', dpi=150); plt.show()