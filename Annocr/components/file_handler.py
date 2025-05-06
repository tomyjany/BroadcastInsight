import os


class FileHandler:
    def __init__(self):
        self.data_folder = "ocr_data/data2"  # Set this to your data folder
        # self.data_folder = "ocr_data/data-ctonly"  # Set this to your data folder
        self.image_files = self._get_image_files()
        self.current_index = 0
        self.ref_file_edited = False  # Track if reference file was edited

    def _get_image_files(self):
        """Fetch all image files that have a corresponding .txt01_ref file but NO .boxes file."""
        files = sorted(os.listdir(self.data_folder))
        image_files = [
            f
            for f in files
            if f.endswith(".jpg")
            and self._has_text_annotation(f)
            and not self._has_bbox_annotation(f)  # Skip images that already have .boxes files
        ]
        return image_files

    def _has_text_annotation(self, image_file):
        """Checks if the corresponding .txt01_ref file exists."""
        text_annotation = self._get_annotation_filename(image_file, "txt01_ref")
        return os.path.isfile(os.path.join(self.data_folder, text_annotation))

    def _has_bbox_annotation(self, image_file):
        """Checks if the corresponding .boxes file exists."""
        text_annotation = self._get_annotation_filename(image_file, "boxes")
        return os.path.isfile(os.path.join(self.data_folder, text_annotation))

    def _get_annotation_filename(self, image_file, extension):
        """Generates the annotation filename for a given image and extension."""
        base_name = os.path.splitext(image_file)[0]
        return f"{base_name}.{extension}"

    def mark_ref_file_edited(self):
        """Mark the reference file as edited."""
        self.ref_file_edited = True

    def save_edited_text_annotations(self, annotations):
        """Don't save edited annotations to a file - only in memory."""
        # Since we're not saving edits to any file, just reset the edited flag
        self.ref_file_edited = False
        return True

    def load_next(self):
        """Loads the next image in the folder."""
        if self.current_index < len(self.image_files) - 1:
            # Check if we need to save edits to the current file
            if self.ref_file_edited:
                print("Warning: Unsaved changes to reference file!")
                
            self.current_index += 1
            self.ref_file_edited = False  # Reset for the new file
            return True
        else:
            return False  # Indicate no more images

    def load_previous(self):
        """Loads the previous image in the folder."""
        if self.current_index > 0:
            # Check if we need to save edits to the current file
            if self.ref_file_edited:
                print("Warning: Unsaved changes to reference file!")
                
            self.current_index -= 1
            self.ref_file_edited = False  # Reset for the new file
            return True
        else:
            return False  # Indicate no previous images

    def get_current_image_path(self):
        """Returns the full path of the current image file."""
        if not self.image_files:
            raise IndexError("No image files found in the data folder.")
        return os.path.join(self.data_folder, self.image_files[self.current_index])

    def get_current_text_annotation_path(self):
        """Returns the full path of the text annotation file.
        If an edited version exists, returns that instead."""
        image_file = self.image_files[self.current_index]
        original_path = os.path.join(
            self.data_folder, self._get_annotation_filename(image_file, "txt01_ref")
        )
        
        # Check if an edited version exists
        edited_path = original_path + ".edited"
        if os.path.exists(edited_path):
            return edited_path
        
        return original_path

    def get_current_original_text_annotation_path(self):
        """Returns the full path of the original text annotation file."""
        image_file = self.image_files[self.current_index]
        return os.path.join(
            self.data_folder, self._get_annotation_filename(image_file, "txt01_ref")
        )

    def get_current_boundary_annotation_path(self):
        """Returns the full path of the boundary box annotation file."""
        image_file = self.image_files[self.current_index]
        boundary_path = os.path.join(
            self.data_folder, self._get_annotation_filename(image_file, "boxes")
        )
        # Ensure the boundary annotation file is initialized (if needed)
        if not os.path.isfile(boundary_path):
            open(boundary_path, "w").close()  # Create an empty file
        return boundary_path
