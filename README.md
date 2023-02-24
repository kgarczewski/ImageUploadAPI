<h2>Image Upload API - Django Rest Framework</h2>

This is an API for uploading and managing images, with different tiers of service available depending on the user's plan.

<h3>Running the Project</h3>
To run the project, first clone the repository from GitHub:

    git clone git@github.com:kgarczewski/ImageUploadAPI.git
Then, navigate to the project directory and use Docker Compose to start the API:
    
    cd ImageUploadAPI
    docker-compose run web python manage.py migrate 
    docker-compose up --build

Once the server is running, you can visit http://127.0.0.1:8000/ to access the API. If you want to create a new user or update an existing one, you can visit http://127.0.0.1:8000/admin. To access the admin panel, you can log in with the following credentials:

- username: admin123
- password: admin
- account tier: Basic

<h3>Uploading Images</h3>

To upload an image, send a POST request to the /images/ endpoint, with the image file attached as a multipart/form-data payload. The API will respond with a JSON object containing the URL of the uploaded image, as well as any thumbnail URLs that apply to the user's plan.

<h3>Listing Images</h3>

To list a user's images, send a GET request to the /images/ endpoint. The API will respond with a JSON object containing a list of image objects, each of which contains the URL of the image as well as any thumbnail URLs that apply to the user's plan.

<h3>User Plans</h3>

The API offers three built-in user plans: Basic, Premium, and Enterprise. The features of each plan are as follows:

<h4>Basic Plan</h4>

Users with the Basic plan can upload images and receive a URL to a thumbnail that is 200 pixels in height.

<h4>Premium Plan</h4>

Users with the Premium plan can upload images and receive the following URLs:

    A thumbnail that is 200 pixels in height
    A thumbnail that is 400 pixels in height
    The original uploaded image

<h4>Enterprise Plan</h4>

Users with the Enterprise plan can upload images and receive the following URLs:

    A thumbnail that is 200 pixels in height
    A thumbnail that is 400 pixels in height
    The original uploaded image
    An expiring URL to the binary image, with the expiration time specified by the user (between 300 and 30000 seconds)

<h4>Custom Plans</h4>

In addition to the built-in plans, admins can create custom plans with the following configurable options:

    Thumbnail sizes
    Presence of the link to the original uploaded file
    Ability to generate expiring links

Admins can manage these custom plans via the Django admin interface.

<h3>API</h3>

The API is implemented using the Django Rest Framework, and is designed to be browsable. There is no custom user interface, as all interaction with the API is done via HTTP requests.

<h3>Testing and Validation</h3>

The API includes tests to ensure that it functions as expected, and input validation is performed to prevent invalid data from being uploaded. Additionally, performance considerations have been taken into account, as the API is designed to handle a large number of images and frequent requests.

Thank you for using our Image Upload API!
