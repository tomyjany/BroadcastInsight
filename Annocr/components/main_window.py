from PyQt5.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QShortcut,
    QLineEdit,
    QGroupBox,
    QFormLayout,
    QStatusBar,
    QFrame,
)
from PyQt5.QtGui import QKeySequence, QFont, QColor
from PyQt5.QtCore import Qt
from Annocr.components.image_canvas import ImageCanvas
from Annocr.components.file_handler import FileHandler


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Guided Annotation Tool")
        self.resize(1200, 800)

        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready to annotate. Select an annotation to begin.")

        # Main layout
        main_widget = QWidget()
        self.layout = QVBoxLayout()
        main_widget.setLayout(self.layout)
        self.setCentralWidget(main_widget)

        # Workflow indicator - shows current step in process
        self.workflow_frame = QFrame()
        self.workflow_frame.setFrameShape(QFrame.StyledPanel)
        self.workflow_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; padding: 10px;")
        workflow_layout = QVBoxLayout(self.workflow_frame)
        
        # Current mode indicator
        self.mode_label = QLabel("CURRENT MODE: VIEWING")
        self.mode_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.mode_label.setAlignment(Qt.AlignCenter)
        self.mode_label.setStyleSheet("color: #0066cc; margin-bottom: 5px;")
        workflow_layout.addWidget(self.mode_label)
        
        # Next action instruction
        self.action_label = QLabel("Waiting for you to select an action...")
        self.action_label.setFont(QFont("Arial", 11))
        self.action_label.setAlignment(Qt.AlignCenter)
        self.action_label.setStyleSheet("color: #006600; font-weight: bold;")
        workflow_layout.addWidget(self.action_label)
        
        self.layout.addWidget(self.workflow_frame)

        # File Handler
        self.file_handler = FileHandler()

        # Add annotation editing area
        self._add_annotation_editor()

        # Image Canvas
        self.canvas = ImageCanvas(self.file_handler, self.annotation_label)
        self.canvas.status_signal.connect(self.update_status)
        self.canvas.mode_changed_signal.connect(self.update_mode)
        self.canvas.annotation_changed_signal.connect(self._update_annotation_editor)
        self.layout.addWidget(self.canvas, 1)  # Give canvas more vertical space

        # Navigation, Skip, Undo, and Save Buttons
        self._add_buttons()

        # Connect signals from canvas
        self._connect_signals()
        
        # Load the first image and annotations
        self._load_image()

    def _add_annotation_editor(self):
        # Create a group box for annotation editing
        editor_group = QGroupBox("Annotation Editor")
        editor_layout = QVBoxLayout()
        
        # Current annotation display
        self.annotation_label = QLabel("Annotation will appear here")
        self.annotation_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px; background-color: #f5f5f5;")
        editor_layout.addWidget(self.annotation_label)
        
        # Mode buttons (tabs)
        mode_buttons = QHBoxLayout()
        
        self.edit_mode_btn = QPushButton("📝 Edit Existing")
        self.edit_mode_btn.setCheckable(True)
        self.edit_mode_btn.setChecked(True)
        self.edit_mode_btn.clicked.connect(lambda: self._switch_mode("edit"))
        self.edit_mode_btn.setStyleSheet("background-color: #e6f7ff;")
        mode_buttons.addWidget(self.edit_mode_btn)
        
        self.add_mode_btn = QPushButton("➕ Add New")
        self.add_mode_btn.setCheckable(True)
        self.add_mode_btn.clicked.connect(lambda: self._switch_mode("add"))
        mode_buttons.addWidget(self.add_mode_btn)
        
        editor_layout.addLayout(mode_buttons)
        
        # Instructions label
        self.instruction_label = QLabel()
        self.instruction_label.setStyleSheet("color: #555; font-style: italic; padding: 5px;")
        editor_layout.addWidget(self.instruction_label)
        
        # Form for editing annotations
        form_layout = QFormLayout()
        
        # Text edit field
        self.annotation_text = QLineEdit()
        self.annotation_text.setPlaceholderText("Enter annotation text here")
        form_layout.addRow("Text:", self.annotation_text)
        
        editor_layout.addLayout(form_layout)
        
        # Buttons for editing - initially we only show the Edit button
        self.edit_buttons_widget = QWidget()
        edit_buttons_layout = QHBoxLayout(self.edit_buttons_widget)
        edit_buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.apply_edit_button = QPushButton("Apply Edit (E)")
        self.apply_edit_button.setToolTip("Edit the current annotation text")
        self.apply_edit_button.clicked.connect(self._apply_annotation_edit)
        self.apply_edit_button.setStyleSheet("background-color: #e6f7ff;")
        edit_buttons_layout.addWidget(self.apply_edit_button)
        
        # Buttons for adding - initially hidden
        self.add_buttons_widget = QWidget()
        add_buttons_layout = QHBoxLayout(self.add_buttons_widget)
        add_buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.add_new_button = QPushButton("Add New Annotation (N)")
        self.add_new_button.setToolTip("Add a new annotation with the entered text")
        self.add_new_button.clicked.connect(self._add_new_annotation)
        self.add_new_button.setStyleSheet("background-color: #ffe6ff;")
        add_buttons_layout.addWidget(self.add_new_button)
        
        editor_layout.addWidget(self.edit_buttons_widget)
        editor_layout.addWidget(self.add_buttons_widget)
        self.add_buttons_widget.hide()  # Hide add button initially
        
        editor_group.setLayout(editor_layout)
        self.layout.addWidget(editor_group)
        
        # Set initial mode
        self._switch_mode("edit")

    def _switch_mode(self, mode):
        """Switch between edit and add modes"""
        if mode == "edit":
            self.edit_mode_btn.setChecked(True)
            self.add_mode_btn.setChecked(False)
            self.edit_buttons_widget.show()
            self.add_buttons_widget.hide()
            self.instruction_label.setText("• Select an annotation from the list\n• Edit the text and click 'Apply Edit'\n• Then draw a bounding box for the annotation")
            self.mode_label.setText("CURRENT MODE: EDITING EXISTING ANNOTATIONS")
            self.mode_label.setStyleSheet("color: #0066cc; font-weight: bold;")
            self.action_label.setText("Step 1: Edit the text (if needed) and click 'Apply Edit'")
        else:  # add mode
            self.edit_mode_btn.setChecked(False)
            self.add_mode_btn.setChecked(True)
            self.edit_buttons_widget.hide()
            self.add_buttons_widget.show()
            self.instruction_label.setText("• Enter text for the new annotation\n• Click 'Add New Annotation'\n• Then draw a bounding box for the new annotation")
            self.mode_label.setText("CURRENT MODE: ADDING NEW ANNOTATIONS")
            self.mode_label.setStyleSheet("color: #660066; font-weight: bold;")
            self.action_label.setText("Step 1: Enter text for the new annotation")
            # Clear the text field when switching to add mode
            self.annotation_text.clear()

    def _add_buttons(self):
        button_layout = QHBoxLayout()

        self.prev_button = QPushButton("Previous (A)")
        self.prev_button.clicked.connect(self._load_previous_image)
        button_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next (D)")
        self.next_button.clicked.connect(self._load_next_image)
        button_layout.addWidget(self.next_button)

        self.skip_button = QPushButton("Skip (S)")
        self.skip_button.setToolTip("Skip the current annotation and move to the next")
        self.skip_button.clicked.connect(self.canvas.skip_current_annotation)
        button_layout.addWidget(self.skip_button)

        self.undo_button = QPushButton("Undo (W)")
        self.undo_button.setToolTip("Undo the last annotation")
        self.undo_button.clicked.connect(self.canvas.undo_last_annotation)
        button_layout.addWidget(self.undo_button)

        self.save_button = QPushButton("Save (Ctrl+S)")
        self.save_button.setToolTip("Save all annotations")
        self.save_button.clicked.connect(self._save_annotations)
        self.save_button.setStyleSheet("background-color: #e6ffe6; font-weight: bold;")
        button_layout.addWidget(self.save_button)

        self.layout.addLayout(button_layout)

        # Shortcuts
        self.prev_shortcut = QShortcut(QKeySequence("a"), self)
        self.prev_shortcut.activated.connect(self._load_previous_image)

        self.next_shortcut = QShortcut(QKeySequence("d"), self)
        self.next_shortcut.activated.connect(self._load_next_image)

        self.skip_shortcut = QShortcut(QKeySequence("s"), self)
        self.skip_shortcut.activated.connect(self.canvas.skip_current_annotation)

        self.undo_shortcut = QShortcut(QKeySequence("w"), self)
        self.undo_shortcut.activated.connect(self.canvas.undo_last_annotation)

        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self._save_annotations)

        # Add new shortcuts for editing
        self.edit_shortcut = QShortcut(QKeySequence("e"), self)
        self.edit_shortcut.activated.connect(self._apply_annotation_edit)
        
        self.add_shortcut = QShortcut(QKeySequence("n"), self)
        self.add_shortcut.activated.connect(self._add_new_annotation)

    def _load_image(self):
        """Loads the current image and updates the annotation canvas."""
        self.canvas.load_image()
        # Update the text field with the current annotation
        self._update_annotation_editor()
        self._switch_mode("edit")  # Reset to edit mode for new images
        self.statusBar.showMessage(f"Loaded image: {self.file_handler.get_current_image_path().split('/')[-1]}")

    def _update_annotation_editor(self):
        """Updates the edit field with the current annotation text."""
        if self.canvas.current_index < len(self.canvas.text_annotations):
            current_text = self.canvas.text_annotations[self.canvas.current_index]
            # Split the annotation to get just the text part (after the colon)
            parts = current_text.split(":", 1)
            if len(parts) > 1:
                # Set the text in the edit field
                self.annotation_text.setText(parts[1].strip())
            else:
                self.annotation_text.setText("")
            
            # Update action guidance
            tag = parts[0].strip()
            self.action_label.setText(f"Working on annotation {tag} - Edit text if needed")
        else:
            self.annotation_text.setText("")
            self.action_label.setText("All annotations complete. You can add new ones or save.")

    def _apply_annotation_edit(self):
        """Applies the edited text to the current annotation."""
        if self.canvas.current_index < len(self.canvas.text_annotations):
            # Get the tag (T1, T2, etc.) and update with new text
            current_text = self.canvas.text_annotations[self.canvas.current_index]
            tag = current_text.split(":", 1)[0].strip()
            new_text = self.annotation_text.text().strip()
            if not new_text:
                self.statusBar.showMessage("Error: Cannot apply empty text. Please enter some text.")
                return
            # Update the annotation in the canvas
            self.canvas.update_current_annotation(f"{tag}: {new_text}")
            # Also update the display label
            self.annotation_label.setText(f"{tag}: {new_text}")
            # Clear the text field to prevent accidental reuse
            self.annotation_text.clear()
            # Update action guidance
            self.action_label.setText(f"Step 2: Draw a bounding box for {tag}")

    def _add_new_annotation(self):
        """Adds a new annotation not present in the original text file."""
        new_text = self.annotation_text.text().strip()
        if not new_text:
            self.statusBar.showMessage("Error: Cannot add empty annotation. Please enter some text.")
            return
        # Create a new tag (T followed by the next number)
        next_tag_num = len(self.canvas.text_annotations)
        new_tag = f"T{next_tag_num}"
        new_annotation = f"{new_tag}: {new_text}"
        # Add to the canvas
        self.canvas.add_new_annotation(new_annotation)
        # Update the display
        self.annotation_label.setText(new_annotation)
        # Clear the text field to prevent accidental reuse
        self.annotation_text.clear()
        # Update action guidance
        self.action_label.setText(f"Step 2: Draw a bounding box for new {new_tag}")

    def _save_annotations(self):
        """Save annotations and show confirmation."""
        success = self.canvas.save_annotation()
        if success:
            self.statusBar.showMessage("Annotations saved successfully!")
            # Flash green background on status bar briefly
            self.statusBar.setStyleSheet("background-color: #90EE90;")
            # Reset after 1.5 seconds
            self.statusBar.setStyleSheet("")
        else:
            self.statusBar.showMessage("Error saving annotations.")

    def update_status(self, message):
        """Updates the status bar with messages from the canvas."""
        self.statusBar.showMessage(message)

    def update_mode(self, mode, details=""):
        """Updates the mode display based on signals from the canvas."""
        if mode == "drawing":
            self.mode_label.setText(f"CURRENT MODE: DRAWING BOUNDING BOX")
            self.mode_label.setStyleSheet("color: #cc0000; font-weight: bold;")
            self.action_label.setText(f"Click and drag to draw box for {details}")
        elif mode == "editing":
            self.mode_label.setText(f"CURRENT MODE: EDITING {details}")
            self.mode_label.setStyleSheet("color: #0066cc; font-weight: bold;")
            self.action_label.setText(f"Edit text for {details} and click 'Apply Edit'")
        elif mode == "done":
            self._switch_mode("edit")  # Reset to edit mode
            self.action_label.setText("All annotations complete. You can add more or save.")

    def _load_next_image(self):
        """Loads the next image if available. Auto-saves current annotations first."""
        # First save the current annotations
        if self.canvas.annotations:
            success = self.canvas.save_annotation()
            if success:
                self.statusBar.showMessage("Annotations saved automatically!")
        
        # Then load the next image
        if self.file_handler.load_next():
            self._load_image()
        else:
            self.statusBar.showMessage("No more images!")

    def _load_previous_image(self):
        """Loads the previous image if available."""
        if self.file_handler.load_previous():
            self._load_image()
        else:
            self.statusBar.showMessage("No previous images!")

    def _connect_signals(self):
        """Connect to canvas signals to update UI when annotations change."""
        self.canvas.annotation_changed_signal.connect(self._update_annotation_editor)
