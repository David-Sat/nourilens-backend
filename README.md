
# NouriLens Backend
by Merve, David, David, and Tayfun for the Google Developer Student Clubs Solution Challenge 2024.

## Overview
We designed NouriLens to tackle malnutrition by making healthier eating habits accessible and affordable, particularly for lower-income families. By leveraging Gemini Pro to extract and enrich information from grocery receipts, it simplifies nutritional tracking and offers personalized, budget-friendly dietary suggestions. Our long-term goal is to facilitate gradual changes in eating habits, challenging the misconception that healthy eating is inherently costly, and ultimately reducing the health inequality gap.

This backend repository, `nourilens-backend`, powers the core functionalities of NouriLens, including receipt analysis, nutritional information extraction, and dietary recommendations, leveraging the FastAPI framework, Gemini Pro Vision, and Gemini Pro.

The Flutter frontend is contained in the submodule `nourilens-ff`.

## Getting Started

### Installation
Install the dependencies:

`pip install -r requirements.txt`

### Running the Server
To start the FastAPI server, run:

`uvicorn main:app --reload`
## Architecture

This project is structured around a serverless architecture, optimized for scalability and efficiency. The backend is built with FastAPI and deployed on Google App Engine, facilitating rapid development and deployment.

### Key Components
- **FastAPI**: Serves as the backbone of the application, handling API requests, processing grocery receipt images, and providing dietary suggestions.
- **Gemini Pro Vision**: Integrated for receipt image analysis and item extraction, enabling the enrichment of grocery items with nutritional information.
- **Firebase Firestore**: Used for storing and synchronizing users' purchase history and personalized suggestions.
- **Google App Engine**: Hosts the FastAPI application, ensuring scalability and reliability.

## Features
- **Receipt Analysis**: Automatically extracts and parses grocery items from uploaded receipt images.
- **Nutritional Information Enrichment**: Enhances grocery items with nutritional insights using Gemini Pro.
- **Personalized Dietary Suggestions**: Offers customized, healthier food alternatives based on users' purchase history and preferences.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
