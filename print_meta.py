import os
import SimpleITK as sitk

data_dir = './data/SR_3/'  # inhale folder
dicom_files = []

for root, dirs, files in os.walk(data_dir):
    for file in files:
        if file.endswith('.dcm'):
            dicom_files.append(os.path.join(root, file))

series_dict = {}
for f in dicom_files:
    img = sitk.ReadImage(f)
    series_uid = img.GetMetaData("0020|000E") if img.HasMetaDataKey("0020|000E") else "unknown"
    if series_uid not in series_dict:
        series_dict[series_uid] = []
    series_dict[series_uid].append(f)

print(f"Found {len(series_dict)} series in {data_dir}")

for uid, files in series_dict.items():
    img0 = sitk.ReadImage(files[0])
    desc = img0.GetMetaData("0008|103e") if img0.HasMetaDataKey("0008|103e") else ""
    protocol = img0.GetMetaData("0018|1030") if img0.HasMetaDataKey("0018|1030") else ""
    print(f"SeriesID: {uid}, #Slices: {len(files)}, Description: {desc}, ProtocolName: {protocol}")
