<p align=center>
<a href="https://fastagi.co"><img src=https://fastagi.co/wp-content/uploads/2023/05/FastAGI_icon.png></a>
</p>

# FastAGI Instagram Tool

The FastAGI Instagram Tool works with the stable diffusion tool, generates an image & caption based on the goals defined by the user and posts it on their instagram business account.Currently will only work on the webapp

## ⚙️ Installation

### 🛠 **Setting Up of FastAGI**
Set up the FastAGI by following the instructions given (https://github.com/KhulnaSoft/FastAGI/blob/main/README.MD)

If you've put the correct Google API key and Custom Search Engine ID, you'll be able to use the Google Search Tool as well.

### 🔧 **Instagram tool requirements**

Since the tool uses the official instagram graph API's to post media on user accounts, There are a few requirements:

You will need access to the following:

    1. An Instagram Business Account or Instagram Creator Account
    2. A Facebook Page connected to that account
    3. A Facebook Developer account that can perform Tasks on that Page
    4. A registered Facebook App with Basic settings configured

Once everything is set up, add the meta user access token (to be generated from facebook developer account), Facebook page ID (can be found on the facebook page connected to the instagram account under 'Page transparency' in 'About' section of the page ) and the stability API key to the correspponding toolkits.

Follow the steps given in the link to set up meta requirements: (https://developers.facebook.com/docs/instagram-api/getting-started)
Follow the link to generate stability API key: (https://dreamstudio.com/api/)

### 🔧 **Configuring in FastAGI Dashboard:**

-You can add your meta user access token and facebook ID to the Instagram Toolkit Page and stability API key to the Image Generation Toolkit Page

## Running FastAGI Instagram Tool

Once everything has been set up just run/schedule an agent with the goal explaining the media to be published and add instagram tool (which will automatically add stable diffusion tool)

## Warning

It is advised to run the instagram tool in restricted mode since it allows you to validate the photos generated. You can schedule agent runs (recurring runs are supported as well). Also, only one photo will be posted to your account in a run. To post multiple photos use recurring runs.