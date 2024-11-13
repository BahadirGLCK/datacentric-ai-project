"""Scripts of the project."""

# %% IMPORTS

import sys
import os
from data.database import handler
from data import utils
import psycopg2
import pandas as pd

# %%
dataset_path = '/Users/bahadirgolcuk/bahadir/project/datacentric-ai-dataset/dock_dataset'
foctory_files_dict = utils.collect_desired_files_and_factory_names_from_dataset_folder(dataset_path, 'annotation')
# %%
foctory_files_dict.keys()

# %%
db_manager = handler.DatabaseManager()
connection = db_manager.connect()
query = """
        SELECT * 
        FROM companies;
        """
row_list = []
with connection.cursor() as cursor:
    cursor.execute(query)
    result = cursor.fetchall()
    row_list.extend(result)
# %%
row_list
# %%
for r in row_list:
    company_name = r[1]
    company_id = r[0]
    for f_name in foctory_files_dict.keys():
        f_name = f_name.lower()
        if company_name in f_name or company_name == f_name:
            if '-' in f_name and not (f_name == 'egger-dekor' or f_name == 'teknik-aluminyum' or f_name == 'norm-civata'):
                c_name = f_name.split('-')[0]
                f_name_splitted = f_name.split('-')[1]



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

# %%
# {device_type}_{factory_name} -> device_id-@0@datetime(W)_
dataset_path = '/Users/bahadirgolcuk/bahadir/project/datacentric-ai-dataset/dock_dataset'
factory_ann_dict = utils.collect_desired_files_and_factory_names_from_dataset_folder(dataset_path, 'annotation')

# %%
factory_ann_dict.keys()
# %%
factory_ann_dict['']
# %%
dataset_path = '/Users/bahadirgolcuk/bahadir/project/datacentric-ai-dataset/dock_dataset'
image_dict = utils.get_information_of_images(dataset_path, 'image')
# %%
list(image_dict.keys())
# %%
image_dict['aka300']

# %%
db_manager = handler.DatabaseManager()
# %%
for key, values in image_dict.items():
    for v in values:
        db_manager.insert_image(v['installation_id'], 
                            v['image_url'],
                            v['is_trainable'], 
                            v['image_resolution'], 
                            v['augmentation'], 
                            v['capture_timestamp'])
# %%
label_list = ['pedestrian_side', 'pedestrian_top', 'truck_back']
for label in label_list:
    db_manager.insert_labels(label)
# %%
import os
bucket_path = '/Users/bahadirgolcuk/bahadir/project/datacentric-ai-project/data/dock'

image_folder = 'image'
annotation_folder = 'annotations'

print(len(os.listdir(os.path.join(bucket_path, image_folder))))
print(len(os.listdir(os.path.join(bucket_path, annotation_folder))))

# %%
# %%
def get_table_as_dataframe(table_name):
    # Database connection parameters
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        port=os.getenv('DB_PORT')
    )
    
    # Query the table
    query = f"SELECT * FROM {table_name};"
    
    # Load data into a DataFrame
    df = pd.read_sql(query, conn)
    
    # Close the connection
    conn.close()
    
    return df
# %%
df_images = get_table_as_dataframe('images')
# %%
len(df_images)
# %%
df_images.columns
# %%
ann_file_url_list = []
for img_url in list(df_images['image_url']):
    filename = img_url.split('/')[-1]
    ann_file_url = 'annotations/' + filename.split('.')[0] + '.xml' 
    ann_file_url_list.append(ann_file_url)
df_images['ann_file_ur'] = ann_file_url_list

# %%
df_images.head()
# %%
list(df_images['image_url'])
# %%
# Database connection parameters
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT"),
)

# Update each row in the database
cursor = conn.cursor()
for _, row in df_images.iterrows():
    cursor.execute(
        "UPDATE images SET ann_file_url = %s WHERE image_id = %s",
        (row['ann_file_ur'], row['image_id'])
    )

conn.commit()  # Commit the transaction
cursor.close()
conn.close()
# %%
