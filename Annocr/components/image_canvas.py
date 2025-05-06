from PyQt5.QtWidgets import QLabel, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QPixmap, QPen, QBrush, QColor, QFont
from PyQt5.QtCore import Qt, QRectF, pyqtSignal


class ImageCanvas(QGraphicsView):
    # Signal to communicate status updates to the main window
    status_signal = pyqtSignal(str)
    # Signal to communicate mode changes to the main window
    mode_changed_signal = pyqtSignal(str, str)
    # Signal for when the current annotation changes
    annotation_changed_signal = pyqtSignal()
    
    def __init__(self, file_handler, annotation_label):
        super().__init__()
        self.file_handler = file_handler
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.current_image = None
        self.annotations = []  # Stores tuples of (label, QGraphicsRectItem)
        self.text_annotations = []  # Stores T1, T2, etc. with text
        self.original_annotations = []  # Stores the original annotations from file
        self.custom_annotations = []  # Stores custom/added annotations
        self.start_point = None
        self.current_rect = None
        self.current_index = 0  # Tracks which text annotation we're on
        self.annotation_label = annotation_label  # QLabel to display the current text
        self.drawing_instruction = None  # Instruction text displayed on the canvas
        self.drawing_mode = False  # Whether we're currently in drawing mode
        
        # Set scene background
        self.scene.setBackgroundBrush(QBrush(QColor(240, 240, 240)))

    def load_image(self):
        """Loads the current image and valid (non-empty) text annotations."""
        self.scene.clear()
        self.annotations.clear()
        self.text_annotations.clear()
        self.original_annotations.clear()
        self.custom_annotations.clear()
        self.current_index = 0  # Start with the first annotation
        self.drawing_mode = False

        # Load the image
        try:
            image_path = self.file_handler.get_current_image_path()
            pixmap = QPixmap(image_path)
            self.current_image = self.scene.addPixmap(pixmap)
            self.fitInView(
                self.current_image, Qt.KeepAspectRatio
            )  # Fit the image to the view
            
            # Add a semi-transparent instruction overlay
            self._add_canvas_instructions("Select annotation to edit or add new annotation")
            
        except IndexError as e:
            self.annotation_label.setText(str(e))
            self.status_signal.emit(f"Error: {str(e)}")
            return

        # Load and filter the text annotations
        self._load_text_annotations()

        # Show the first annotation text
        self._update_current_annotation_label()
        # Emit signal that annotation has changed when loading a new image
        self.annotation_changed_signal.emit()

    def _add_canvas_instructions(self, text):
        """Adds minimal instruction text to the canvas."""
        if hasattr(self, 'instruction_text') and self.instruction_text in self.scene.items():
            self.scene.removeItem(self.instruction_text)
        
        # Keep instruction background but make it smaller
        self.instruction_text = QGraphicsTextItem(text)
        self.instruction_text.setFont(QFont("Arial", 12))
        self.instruction_text.setDefaultTextColor(QColor(0, 0, 255, 200))
        
        # Position at the top center of the view
        rect = self.instruction_text.boundingRect()
        scene_rect = self.sceneRect()
        x_pos = (scene_rect.width() - rect.width()) / 2
        self.instruction_text.setPos(x_pos, 10)
        
        self.scene.addItem(self.instruction_text)

    def _load_text_annotations(self):
        """Loads and filters text annotations from the reference file."""
        text_path = self.file_handler.get_current_text_annotation_path()
        with open(text_path, "r") as f:
            raw_annotations = [line.strip() for line in f.readlines()]
            # Filter out empty annotations
            valid_annotations = [
                t for t in raw_annotations if t and ":" in t and t.split(":")[1].strip()
            ]
            self.text_annotations = valid_annotations
            # Store the original annotations for reference
            self.original_annotations = valid_annotations.copy()
        
        if len(self.text_annotations) > 0:
            self.status_signal.emit(f"Loaded {len(self.text_annotations)} annotations from reference file.")
            # Signal mode change
            if self.current_index < len(self.text_annotations):
                tag = self.text_annotations[self.current_index].split(":", 1)[0].strip()
                self.mode_changed_signal.emit("editing", tag)
        else:
            self.status_signal.emit("No annotations found in reference file. You can add new annotations.")
            self.mode_changed_signal.emit("done", "")

    def _update_current_annotation_label(self):
        """Updates the QLabel to show the current text annotation."""
        if self.current_index < len(self.text_annotations):
            current_text = self.text_annotations[self.current_index]
            self.annotation_label.setText(current_text)  # Display the annotation (e.g., "T1: Hello")
            
            # Update instructions on canvas - but with minimal text
            tag = current_text.split(":", 1)[0].strip()
            if self.drawing_mode:
                self._add_canvas_instructions(f"Draw box for {tag}")
            else:
                # Signal mode change to editing without adding text to canvas
                self.mode_changed_signal.emit("editing", tag)
            
        else:
            self.annotation_label.setText("All annotations complete!")
            self._add_canvas_instructions("All annotations complete")
            # Signal mode change to done
            self.mode_changed_signal.emit("done", "")

    def update_current_annotation(self, new_text):
        """Updates the text of the current annotation."""
        if self.current_index < len(self.text_annotations):
            # Update the text annotation
            self.text_annotations[self.current_index] = new_text
            
            # If this is an original annotation, mark it as edited
            if self.current_index < len(self.original_annotations):
                # Store that we've edited this annotation
                self.file_handler.mark_ref_file_edited()
            
            # Set drawing mode
            self.drawing_mode = True
            tag = new_text.split(":", 1)[0].strip()
            self._add_canvas_instructions(f"Draw box for {tag}")
            self.status_signal.emit(f"Now draw a bounding box for annotation {tag}")
            
            # Signal mode change to drawing
            self.mode_changed_signal.emit("drawing", tag)
                
            self._update_current_annotation_label()
            return True
        return False

    def add_new_annotation(self, new_annotation):
        """Adds a new annotation not present in the original file."""
        self.text_annotations.append(new_annotation)
        self.custom_annotations.append(new_annotation)
        
        # Switch to the new annotation for drawing a box
        self.current_index = len(self.text_annotations) - 1
        
        # Set drawing mode
        self.drawing_mode = True
        tag = new_annotation.split(":", 1)[0].strip()
        self._add_canvas_instructions(f"Draw box for new {tag}")
        self.status_signal.emit(f"Now draw a bounding box for new annotation {tag}")
        
        # Signal mode change to drawing
        self.mode_changed_signal.emit("drawing", tag)
        
        self._update_current_annotation_label()
        return True

    def mousePressEvent(self, event):
        """Start drawing a bounding box."""
        if event.button() == Qt.LeftButton and self.current_index < len(self.text_annotations):
            # Only respond to mouse events if we're in drawing mode
            if not self.drawing_mode:
                return
                
            self.setCursor(Qt.CrossCursor)  # Change cursor to indicate drawing
            self.start_point = self.mapToScene(event.pos())
            
            # If we already have a temporary rectangle, remove it
            if hasattr(self, 'temp_rect') and self.temp_rect in self.scene.items():
                self.scene.removeItem(self.temp_rect)
                
            # Create a new temporary rectangle
            self.temp_rect = QGraphicsRectItem(QRectF(self.start_point, self.start_point))
            self.temp_rect.setPen(QPen(Qt.green, 2, Qt.DashLine))
            self.scene.addItem(self.temp_rect)
            
            # Update status
            tag = self.text_annotations[self.current_index].split(":", 1)[0].strip()
            self.status_signal.emit(f"Drawing box for {tag}. Release mouse to complete.")

    def mouseMoveEvent(self, event):
        """Update the temporary rectangle as mouse moves."""
        if event.buttons() & Qt.LeftButton and self.start_point and self.drawing_mode:
            current_point = self.mapToScene(event.pos())
            if hasattr(self, 'temp_rect') and self.temp_rect in self.scene.items():
                self.temp_rect.setRect(QRectF(self.start_point, current_point).normalized())

    def mouseReleaseEvent(self, event):
        """Finish drawing a bounding box."""
        if event.button() == Qt.LeftButton and self.start_point and self.drawing_mode:
            self.setCursor(Qt.ArrowCursor)  # Restore cursor
            end_point = self.mapToScene(event.pos())
            
            # Remove temporary rectangle
            if hasattr(self, 'temp_rect') and self.temp_rect in self.scene.items():
                self.scene.removeItem(self.temp_rect)
            
            # Create final rectangle
            rect = QRectF(self.start_point, end_point).normalized()
            
            # Only create a rectangle if it has some size
            if rect.width() > 5 and rect.height() > 5:
                self.current_rect = QGraphicsRectItem(rect)
                self.current_rect.setPen(QPen(Qt.green, 2))
                self.scene.addItem(self.current_rect)

                # Associate the bounding box with the current annotation text
                if self.current_index < len(self.text_annotations):
                    current_text = self.text_annotations[self.current_index]
                    self.annotations.append(
                        (current_text, self.current_rect)
                    )
                    
                    # Add a tag label to the box
                    tag = current_text.split(":", 1)[0].strip()
                    tag_item = QGraphicsTextItem(tag)
                    tag_item.setDefaultTextColor(Qt.green)
                    tag_item.setFont(QFont("Arial", 10, QFont.Bold))
                    tag_item.setPos(rect.topLeft())
                    self.scene.addItem(tag_item)
                    
                    self.status_signal.emit(f"✅ Bounding box added for {tag}")
                    self.drawing_mode = False
                    
                    # Move to the next annotation
                    self._move_to_next_annotation()
            else:
                self.status_signal.emit("⚠️ Error: Bounding box too small. Please try again.")
                self.start_point = None

    def _move_to_next_annotation(self):
        """Moves to the next valid annotation."""
        self.current_index += 1
        self.start_point = None
        self.drawing_mode = False
        self._update_current_annotation_label()
        
        # Emit signal that annotation has changed so UI can update
        self.annotation_changed_signal.emit()
        
        if self.current_index < len(self.text_annotations):
            tag = self.text_annotations[self.current_index].split(":", 1)[0].strip()
            self.status_signal.emit(f"Moving to next annotation: {tag}")
            # Signal mode change to editing
            self.mode_changed_signal.emit("editing", tag)
        else:
            self.status_signal.emit("All annotations complete! You can add more or save.")
            # Signal mode change to done
            self.mode_changed_signal.emit("done", "")

    def skip_current_annotation(self):
        """Skips the current annotation and moves to the next."""
        if self.current_index < len(self.text_annotations):
            tag = self.text_annotations[self.current_index].split(":", 1)[0].strip()
            self.status_signal.emit(f"Skipped annotation {tag}")
        self._move_to_next_annotation()
        # Annotation has changed after skipping
        self.annotation_changed_signal.emit()

    def undo_last_annotation(self):
        """Removes the most recent bounding box annotation."""
        if self.annotations:
            # Remove the last bounding box from the scene
            label, last_rect = self.annotations.pop()
            self.scene.removeItem(last_rect)
            
            # Find and remove the corresponding tag label
            tag = label.split(":", 1)[0].strip()
            for item in self.scene.items():
                if isinstance(item, QGraphicsTextItem) and item.toPlainText() == tag:
                    self.scene.removeItem(item)
                    break

            # Revert the current index to the previous annotation
            self.current_index = max(0, self.current_index - 1)
            self.status_signal.emit(f"⬅️ Undid last annotation ({tag})")
            self.drawing_mode = False

            # Update the label to reflect the current text annotation
            self._update_current_annotation_label()
            # Annotation has changed after undoing
            self.annotation_changed_signal.emit()

    def save_annotation(self):
        """Saves bounding box annotations to the .boxes file."""
        # Save bounding boxes
        boundary_path = self.file_handler.get_current_boundary_annotation_path()
        try:
            with open(boundary_path, "w") as f:
                for label, rect_item in self.annotations:
                    rect = rect_item.rect()
                    # Get just the tag part (T1, T2, etc.)
                    tag = label.split(":", 1)[0].strip()
                    # Get the text part (after the colon)
                    text = label.split(":", 1)[1].strip() if ":" in label else ""
                    f.write(
                        f"{tag} {text} {rect.x()} {rect.y()} {rect.width()} {rect.height()}\n"
                    )
            
            # Note that we don't save any edited ref files
            self.status_signal.emit(f"✅ Saved {len(self.annotations)} annotations to {boundary_path}")
            return True
            
        except Exception as e:
            self.status_signal.emit(f"❌ Error saving annotations: {str(e)}")
            return False

    def resizeEvent(self, event):
        """Handle resize event to maintain view of the image."""
        super().resizeEvent(event)
        if self.current_image:
            self.fitInView(self.current_image, Qt.KeepAspectRatio)
