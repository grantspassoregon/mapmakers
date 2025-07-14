Logging into ArcGIS
===================


* Obtain a client id.
* Save the client id to a ``.env`` file in your working directory.
* Run the login script in "/exmaples/grants_pass/login.py".
* Import ``mapmakers`` into a build script for your new Webmap.
* Run the build script.

Obtain a Client ID
------------------

The instructions to obtain a client ID come from the "User authentication with OAuth 2.0" section from `this page`_.
    The steps below show how a client id can be obtained by registering a new application with you GIS.  Only one client id is required, so if your GIS has one already, you may use it instead of creating a new application.
    
    * Log in to your ArcGIS Online or ArcGIS Enterprise organization.
    * Go to the Content tab.
    * Click 'New item', then select 'Application'.
    * On the 'New item' dialog, select 'Other application' and click 'Next'.
    * Type in a title for the application item.  Optionally, specify the folder, tags and summary.
    * Click 'Save' to add the item.
    * On the item details page of this newly created application, browse to the Credentials section and find the Client ID.  The string listed is the value that you will pass in as the ``client_id`` parameter when creating the GIS object.

.. _`this page`: https://developers.arcgis.com/python/guide/working-with-different-authentication-schemes/#Web-tier-authentication-secured-with-IWA

Setting Up the ``.env`` File
----------------------------

The client ID is an example of a form of credentials that is not easy to memorize. However, entering the client ID directly into our code would be insecure.  Anybody on Github could steal your credentials.  *Environmental variables* are a way to store these sensitive credentials on your local machine, and load them into the workspace later when needed.  The convention is to keep these variables stored in a file called ``.env``.  The dot at the beginning of the file name denotes that it is a hidden file, and will not appear by default within File Explorer on Windows.

At the start of the login scripts at "/examples/grants_pass/login.py", we use the following import statement and function call:

.. code-block:: python

   from dotenv import load_dotenv
   
   load_dotenv()

The *load_dotenv* function from the ``dotenv`` package will read the contents of the ``.env`` file and allow you to access the variables that it defines.  In this case, we are storing the client id as an environmental variable named ``CLIENT_ID``.  We specify the value of an environmental variable using the variable name, followed by an equal sign, followed by the value wrapped in quotes.

Here is an example of how to define the ``CLIENT_ID`` variable in a ``.env`` file:

.. code-block:: console

   CLIENT_ID="my_client_id"

Replace *"my_client_id"* with the actual value of your client ID.

The ``.env`` file will not exist in your project until you create it.  Use the text editor of your choice, and make sure to include the dot before *env* for the title.  If the text editor sneakily adds a ".txt" or some other extension on the end of the file name, rename the file as ``.env`` and ignore any cautionary warnings about changing the file type.

.. _login_script:

Running the Login Script
------------------------

In it's entirety, the login script consists of:

.. code-block:: python

   from arcgis.gis import GIS
   from dotenv import load_dotenv
   import os
   import logging

   logging.basicConfig(
       format="%(asctime)s %(message)s",
       datefmt="%m/%d/%Y %I:%M:%S %p",
       level=logging.INFO,
   )

   load_dotenv()
   PORTAL = "https://grantspassoregon.maps.arcgis.com/"
   CLIENT_ID = os.getenv("CLIENT_ID")
   logging.info("Environmental variables loaded.")
   GIS_CONN = GIS(PORTAL, client_id=CLIENT_ID)

The import statements tell us that we are using the *GIS* class from the *arcgis* Python API, as well as *load_dotenv*, the *os* package, and the *logging* package.  The next block configures logging to include the date and time of the message.

After loading our environmental variables with *load_dotenv()*, we define the portal path as *PORTAL*.  If you instead use the path for our internal portal ("https://gis.grantspassoregon.gov/arcgis/home"), make sure that you obtain your client ID from the internal portal and not AGOL.  This example is configured to use AGOL.

Note that *load_dotenv* does not do the whole job of reading your environmental variables into the workspace, you will still need to access the value by calling *os.getenv()*.  As an argument, *os.getenv* takes the name of the variable that you have defined in your ``.env``, in this case "CLIENT_ID".

When the last line of the script executes, it will attempt to open a GIS connection and save that connection as the variable *GIS_CONN*. ESRI describes this process as an "interactive login experience".  First the terminal will prompt you to authenticate using SAML, reading:

.. code-block:: console

   Enter code obtained on signing in using SAML:

A browser window will then open leading to a plain-Jane web page with the heading **OAuth2 Approval**.  The instructions will read "Please copy this code, switch to you application and paste it there:" and below will be a text field with a long string of text.  Copy this text, switch back to the terminal, and paste the authentication string there.  If you are using `Windows Terminal`_, pressing ``Ctrl`` + ``Shift`` + ``v`` will paste the text.

.. _`Windows Terminal`: https://learn.microsoft.com/en-us/windows/terminal/

Note that at the time of writing, after pressing ``Enter`` you will receive an *InsecureRequestWarning* advising you to add certificate verification.  You can safely ignore this warning, as we are logging in using the recommended method from ESRI.  Addressing this warning is a concern for the maintainers of the *arcgis* Python API.

Upon successful completion, this script will add the variable *gis* to your Python environment, which holds a reference to the authenticated GIS connection.  The ``mapmakers`` library assumes the existence of the *GIS_CONN* variable.  If the GIS connection is not named *GIS_CONN*, or if you forget to run the login script prior to using the library, you will receive an error message that *GIS_CONN* is unassigned.  Admittedly, this device is a bit a crude hack to get around the restrictions of multi-factor authentication, and it is not best practice to use a variable in a library that is not necessarily assigned.  I am open to ideas for a better way to do this.

To execute the login script, navigate to the ``mapmakers`` package location on your machine and open a session of Python from the terminal:

.. code-block:: console

   cd path/to/mapmakers
   python

In the Python interactive shell, enter the following command:

.. code-block:: python

   > exec(open("examples/grants_pass/login.py")).read())

If your working directory is different than the location for the ``mapmakers`` package, you will need to adjust the path to the login script.  The *open* command specifies for Python to open the file at the indicated path, and the *read* methods reads the contents of the file into memory.  The *exec* command executes any commands contained in the contents of the file.  We make use of this pattern to read and execute scripts from the Python shell.


Import ``mapmakers`` Into Your Build Script
-------------------------------------------

The build script is a python file that contains the instructions for building your Webmap.  This script is where you will import and use the ``mapmakers`` package.  To learn more about how to use the classes and methods in the ``mapmakers`` package, see :doc:`making_maps`.

Import ``mapmakers`` into your script the same way you would any other package:

.. code-block:: python

   import mapmakers as m

Place the import statement at the top of the file.  Here we have assigned the alias `m` to the package name using *as*.


Running Your Build Script
-------------------------

Run your build script using the same pattern that we used for the login script.  From the Python interactive shell, enter the command:

.. code-block:: python

   > exec(open("path/to/my/script.py").read())

Replace *"path/to/my/script.py"* with the absolute or relative path to your build script.  Make sure that you have logged in first using the :ref:`login script<login_script>`, or the ``mapmakers`` package will throw an error that *GIS_CONN* is undefined.
