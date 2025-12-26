# The COVID-19 Effect: From Panic to Burnout
## A Behavioral Analysis of Mental Health Communities on Reddit (Jan-Apr 2020)

**Author:** Nykyta Babakov  
**Course:** Computational Social Science  
**Date:** December 2025  

---

## 📌 Project Overview

This project analyzes over **4 million Reddit posts** from mental health and COVID-19 specific communities to understand how the onset of the pandemic altered online social behavior.

Using **Natural Language Processing (TextBlob)** and temporal data analysis, we identified a distinct shift from personal storytelling to "emotional numbness" and news consumption during the early months of 2020.

### Key Insights:
* **The "Shock" Phase:** Activity spikes correlated perfectly with global lockdowns (March 2020).
* **Emotional Burnout:** A significant decline in linguistic subjectivity and emotional tone was observed as the crisis progressed.
* **Engagement Paradox:** Objective facts were largely ignored; the community rewarded highly subjective, emotional content (Negativity Bias).

---

## 📂 Dataset Link

The analysis is based on a large-scale dataset aggregated from Reddit.  
👉 [https://ukmaedu-my.sharepoint.com/:x:/g/personal/n_babakov_ukma_edu_ua/IQCpG1F1ODOQRbrq9dEex_NjAZDk8efrINbF8Ao4WGxKizw?e=vf26iL]

---

## 📂 Repository Structure

* `eda1.ipynb` - The main Jupyter Notebook containing Data Cleaning, EDA, Sentiment Analysis, and Visualization code.
* `requirements.txt` - List of Python dependencies required to run the project.
* `6_13.pdf` - Final presentation slides summarizing the research.

---

## 🚀 How to Run

To replicate the analysis, follow these steps strictly. The project requires **Python 3.8+**.

### 1. Clone the Repository
Download the code to your local machine:
```bash
git clone [https://github.com/NykytaBabakov/CSS-2025.git](https://github.com/NykytaBabakov/CSS-2025.git)
cd CSS-2025
```

### 2. Set Up a Virtual Environment (Recommended)
Isolating dependencies prevents conflicts with your system packages:
```bash
# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the environment (Linux/MacOS)
source venv/bin/activate

# For Windows users:
# venv\Scripts\activate
```

### 3. Install Dependencies
Install all necessary libraries (pandas, numpy, textblob, seaborn, etc.):
```bash
pip install -r requirements.txt
```
> **Note:** If you encounter errors related to TextBlob corpora, run this command to download the necessary NLTK data:
```bash
python -m textblob.download_corpora
```

### 4. Download and Place the Dataset
**Important:** The raw dataset is **not** included in the repository due to file size limits.
1. Download the dataset file from the [https://ukmaedu-my.sharepoint.com/:x:/g/personal/n_babakov_ukma_edu_ua/IQCpG1F1ODOQRbrq9dEex_NjAZDk8efrINbF8Ao4WGxKizw?e=vf26iL].
2. Move the downloaded `.csv` file into the **root directory** of this project.

### 5. Run the Jupyter Notebook
Launch the notebook environment:
```bash
jupyter notebook
```
Open `eda1.ipynb` and click **"Run All"** to reproduce the data cleaning, analysis, and visualization steps.
