---

# Image Processing and Analysis Pipeline

This repository contains an image processing pipeline integrated with a **Python backend** and a **Ruby on Rails frontend**. The pipeline processes input images, applies segmentation, refines blobs, and analyzes object distributions, with results displayed in a user-friendly web application.

---

## Features

1. **Image Preprocessing**: Gaussian smoothing and Otsu thresholding for object segmentation.
2. **Blob Refinement**: Morphological transformations and median filtering for clean masks.
3. **Object Analysis**: Calculate object dimensions and visualize distributions (widths and heights).
4. **Backend**: A Python Flask server handles the image processing and runs the pipeline.
5. **Frontend**: A Ruby on Rails web app allows users to upload images and view results in a modal popup.

---

## Prerequisites

Before setting up the repository, ensure the following dependencies are installed:

### General Requirements
- Python 3.7+
- Ruby 3.0+
- Rails 7.0+

### Python Backend Requirements
Install the Python dependencies in a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

The `requirements.txt` file includes:
- OpenCV
- NumPy
- Matplotlib
- Seaborn
- Flask
- SciPy

### Ruby Frontend Requirements
Install the necessary Ruby gems:
```bash
cd frontend
bundle install
```

---

## Setting Up the Project

### 1. Clone the Repository
```bash
git clone https://github.com/samgbsr/Myotube_Predictor/
cd your-repo-name
```

### 2. Start the Python Backend
The Python backend handles image processing. To run it:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
flask run
```
The backend runs on `http://127.0.0.1:5000`.

### 3. Start the Ruby Frontend
The Ruby on Rails frontend interacts with the Python backend and serves the web app. To start it:
```bash
cd frontend
rails server
```
The frontend runs on `http://127.0.0.1:3000`.

---

## Usage

1. **Web Interface**:
   - Open `http://127.0.0.1:3000` in your browser.
   - Upload an image using the provided form.
   - View the processed results in a modal popup, including the refined mask and masked image.

2. **Backend**:
   - The Python backend processes uploaded images and returns refined masks, masked images, and object statistics.

3. **Results**:
   - Saved results are stored in the `resultados/` folder in the Python backend directory.
   - The frontend displays processed outputs dynamically.

---

## Folder Structure

```plaintext
.
├── backend/           # Python backend
│   ├── app.py                # Flask application entry point
│   ├── requirements.txt      # Python dependencies
│   ├── static/               # Processed images and results
│   └── Modelo/               # Trained model and prediction scripts
├── frontend/            # Ruby on Rails frontend
│   ├── app/                  # Rails application files
│   ├── Gemfile               # Ruby gem dependencies
│   └── db/                   # Rails database files
├── README.md                 # Project documentation (this file)
```

---

## API Endpoints

### Python Backend
- **POST `/process`**:
  - Input: Image file (uploaded via multipart form-data).
  - Output: Processed images and object dimensions.

### Ruby Frontend
- **Form Submission**:
  - Uses Axios to upload files to the Python backend.
  - Displays processed results in a Bootstrap modal.

---

## Troubleshooting

- **Backend Issues**:
  - Ensure the Python environment is activated before running `flask run`.
  - Check for missing dependencies in `requirements.txt`.

- **Frontend Issues**:
  - Ensure all gems are installed using `bundle install`.
  - Restart the Rails server if encountering runtime errors.

- **Connection Issues**:
  - Verify both backend (`http://127.0.0.1:5000`) and frontend (`http://127.0.0.1:3000`) are running.
  - Ensure the frontend correctly points to the backend URL in the configuration.

---

## Future Enhancements

- Integrate a database to store processing results permanently.
- Add user authentication to the Rails app.
- Extend the pipeline to handle additional image types or analysis.

---

## License

This project is licensed under the MIT License.

---

## Data and Privacy

The project is implemented in a standalone web application that can be run on localhost with the purpose of not connecting to the internet or needing to upload images anywhere on the web. Te database is created locally when de project is first executed and remains there during use.
