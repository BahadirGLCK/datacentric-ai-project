"""Scripts of the project."""

# %% IMPORTS

import sys
import os
from data.database import handler
from data import utils

# %%
dataset_path = '/Users/bahadirgolcuk/bahadir/project/datacentric-ai-dataset/dock_dataset'
foctory_files_dict = utils.collect_desired_files_and_factory_names_from_dataset_folder(dataset_path, 'annotation')
# %%
foctory_files_dict.keys()

# %%
foctory_device_dict = {}
for key, values in foctory_files_dict.items():
    foctory_device_dict[key] = []
    for v in values:
        device_id = v.split('/')[-1][:8]
        if not device_id in foctory_device_dict[key]:
            foctory_device_dict[key].append(device_id)
# %%
foctory_device_dict.keys()
# %%
db_manager = handler.DatabaseManager()
connection = db_manager.connect()
query = """
        SELECT * 
        FROM factories;
        """
row_list = []
with connection.cursor() as cursor:
    cursor.execute(query)
    result = cursor.fetchall()
    row_list.extend(result)
# %%
row_list
# %%
from datetime import datetime
default_installation_date = datetime.strptime("2024-09-09", "%Y-%m-%d").date()
# %%
device_type_id = '49495482-d2ab-452f-9a9d-eb2df0f6ec2d'
installation_date = default_installation_date
is_test_device = False
is_installed = False
is_data_collector = False
for key, device_id_list in foctory_device_dict.items():
    for r in row_list:
        if r[2] in key:
            factory_id = r[0]
            for device_id in device_id_list:
                db_manager.insert_installation( device_type_id, 
                                                factory_id, 
                                                is_test_device, 
                                                is_installed, 
                                                is_data_collector, 
                                                installation_date,
                                                device_id)
# %%
dataset_path = '/Users/bahadirgolcuk/bahadir/project/datacentric-ai-dataset/dock_dataset'
factory_ann_dict = utils.collect_desired_files_and_factory_names_from_dataset_folder(dataset_path, 'annotation')
counter_ann = 0
for k, v in factory_ann_dict.items():
    counter_ann += len(v)
factory_img_dict = utils.collect_desired_files_and_factory_names_from_dataset_folder(dataset_path, 'image')
counter_img = 0
for k, v in factory_img_dict.items():
    counter_img += len(v)

print(counter_ann)
print(counter_img)


# %%
factory_ann_dict.keys()
# %%
from collections import Counter

for k, v in factory_ann_dict.items():
    counted_items = Counter(v)
    more_times_items = [item for item, count in counted_items.items() if count >= 2]
    print(f'{k}: {more_times_items}')
# %%
from collections import Counter

for k, v in factory_img_dict.items():
    counted_items = Counter(v)
    more_times_items = [item for item, count in counted_items.items() if count >= 2]
    print(f'{k}: {more_times_items}')
# %%

all_ann_files = []
for k,v in factory_ann_dict.items():
    all_ann_files.extend(v)

# %%
all_img_files = []
for k,v in factory_img_dict.items():
    all_img_files.extend(v)
# %%
len(all_ann_files), len(all_img_files)
# %%
all_ann_fname_list = [fpath.split('/')[-1] for fpath in all_ann_files]
all_img_fname_list = [fpath.split('/')[-1] for fpath in all_img_files]

print(len(all_ann_fname_list))
print(len(all_img_fname_list))
# %%

counted_items = Counter(all_ann_fname_list)
more_times_ann_items = [item for item, count in counted_items.items() if count >= 2]

counted_items = Counter(all_img_fname_list)
more_times_img_items = [item for item, count in counted_items.items() if count >= 2]

print(len(more_times_ann_items))
print(len(more_times_img_items))
# %%
more_times_ann_items

# %%
from data.bucket.handler import MinIOClient
# %%
minio_client = MinIOClient(bucket_name = 'dock')

# upload images
for ann_path in all_ann_files:
    dest_path = 'annotations/' + ann_path.split('/')[-1]
    minio_client.upload_file(ann_path, dest_path)

# %%
# upload images
for img_path in all_img_files:
    dest_path = 'image/' + img_path.split('/')[-1]
    minio_client.upload_file(img_path, dest_path)
# %%
minio_client.count_files()