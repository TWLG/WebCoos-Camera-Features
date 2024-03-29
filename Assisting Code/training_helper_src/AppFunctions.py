import os
import shutil
from sklearn.model_selection import train_test_split


class AppFunctions:

    def split_into_train_test_vali(path, train=70, test=20, validate=10):

        if (train + test + validate) != 100:
            return "The sum of train, test and validate proportions should be 100"

        train = train / 100
        test = test / 100
        validate = validate / 100

        base_path = path + "/images/"
        dataset_copy_path = path + "/training_split_output/"

        classes = [d for d in os.listdir(
            base_path) if os.path.isdir(os.path.join(base_path, d))]

        # Create train, test, validate directories
        splits = ['train', 'test', 'val']
        for s in splits:
            os.makedirs(os.path.join(dataset_copy_path, s), exist_ok=True)
            for class_ in classes:
                os.makedirs(os.path.join(
                    dataset_copy_path, s, class_), exist_ok=True)

        for class_ in classes:
            class_path = os.path.join(base_path, class_)
            images = [f for f in os.listdir(class_path) if f.endswith(
                '.jpg') or f.endswith('.png')]

            # Shuffle and split
            train_val, test_files = train_test_split(
                images, test_size=test, random_state=42)
            train_files, val_files = train_test_split(
                train_val, test_size=validate/(train+validate), random_state=42)

            # Function to copy files
            def copy_files(files, split):
                for file in files:
                    src_path = os.path.join(base_path, class_, file)
                    dst_path = os.path.join(
                        dataset_copy_path, split, class_, file)
                    shutil.copy(src_path, dst_path)

            # Copy files to their respective directories
            copy_files(train_files, 'train')
            copy_files(test_files, 'test')
            copy_files(val_files, 'validate')

            print(f"Processed class {class_}: {len(train_files)} train, {
                  len(test_files)} test, {len(val_files)} validate files.")
