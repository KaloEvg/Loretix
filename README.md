# Movie and Series Management Project

This repository contains a simple web application that allows users to manage a list of movies and series. The application supports adding, modifying, deleting, and viewing content, using an SQLite database for data storage.

## Repository Content

### HTML Files
- **`add_contenido.html`**: Form for adding content to the database.
- **`add_destacadas.html`**: Page for adding featured content.
- **`agregar.html`**: Interface for adding new movie or series entries.
- **`base.html`**: Base template containing the general design of the website.
- **`borrar_contenido.html`**: Interface for deleting content from the database.
- **`detalle.html`**: Details page for a movie or series.
- **`index.html`**: Main page of the application.
- **`login.html`**: Login form.
- **`mi_lista.html`**: Page displaying the user's personalized list.
- **`modificar_contenido.html`**: Form for modifying existing content.
- **`peliculas.html`**: List of all available movies.
- **`plantilla.html`**: Reusable template for other pages.
- **`registro.html`**: Registration form for new users.
- **`series.html`**: List of all available series.

### Application-Related Files
- **`main.py`**: Main file containing the application code. This file handles the routes and business logic.
- **`base_datos.db`**: SQLite database storing the information about movies and series.
- **`estilos.css`**: CSS file defining the application's appearance.
- **`background.png`**, **`logo.png`**, **`icon.ico`**: Graphic files used in the user interface.

### Directories
- **`Peliculas`**: Folder possibly containing images or information related to movies.
- **`Series`**: Folder possibly containing images or information related to series.

## Requirements
To run this application, you need:
- Python 3.x
- Flask (web framework)

## Installation
1. Clone the repository:
   ```bash
   git clone <REPOSITORY_URL>
   ```
2. Navigate to the project directory:
   ```bash
   cd <DIRECTORY_NAME>
   ```
3. Install the required dependencies:
   ```bash
   pip install flask
   ```

## Execution
1. Run the `main.py` file:
   ```bash
   python main.py
   ```
2. Open your browser and go to `http://localhost:5000` to use the application.

## Main Features
- **Add Content**: Allows users to add new movies or series.
- **Modify Content**: Users can edit the information of existing movies or series.
- **Delete Content**: Users can delete movies or series from the database.
- **View Details**: Users can view detailed information about each movie or series.
- **Personalized List**: Registered users can maintain a personalized list of content.

## Database Structure
The `base_datos.db` database contains the following main tables:
- **Users**: Information about registered users.
- **Content**: Information about movies and series.

## Customization
You can customize the design by modifying the `estilos.css` file and changing the images in `background.png`, `logo.png`, and `icon.ico`.

## Contribution
If you want to contribute to this project:
1. Fork the repository.
2. Create a branch with your new feature:
   ```bash
   git checkout -b new-feature
   ```
3. Make your changes and commit them:
   ```bash
   git commit -m "Add new feature"
   ```
4. Push your branch:
   ```bash
   git push origin new-feature
   ```
5. Open a Pull Request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact
If you have questions or suggestions, feel free to open an issue or contact the project maintainer at kaloyaneg@gmail.com
