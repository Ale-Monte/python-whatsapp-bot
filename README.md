# **Deploy AI WhatsApp Bot for Small Grocery Stores with Pure Python**

# Set Up Whatsapp API

This guide will walk you through the process of creating a WhatsApp bot using the Meta (formerly Facebook) Cloud API with pure Python, and Flask particularly. We'll also integrate webhook events to receive messages in real-time and use OpenAI to generate AI responses and then deploy it to Microsoft Azure.

## Prerequisites

1. A Meta developer account — If you don’t have one, you can [create a Meta developer account here](https://developers.facebook.com/).
2. A business app — If you don't have one, you can [learn to create a business app here](https://developers.facebook.com/docs/development/create-an-app/). If you don't see an option to create a business app, select **Other** > **Next** > **Business**.
3. Familiarity with Python to follow the tutorial.

## Table of Contents

- [Build AI WhatsApp Bots with Pure Python](#build-ai-whatsapp-bots-with-pure-python)
  - [Prerequisites](#prerequisites)
  - [Table of Contents](#table-of-contents)
  - [Get Started](#get-started)
  - [Step 1: Select Phone Numbers](#step-1-select-phone-numbers)
  - [Step 2: Send Messages with the API](#step-2-send-messages-with-the-api)
  - [Step 3: Configure Webhooks to Receive Messages](#step-3-configure-webhooks-to-receive-messages)
    - [Start your app](#start-your-app)
    - [Launch ngrok](#launch-ngrok)
    - [Integrate WhatsApp](#integrate-whatsapp)
    - [Testing the Integration](#testing-the-integration)
  - [Step 4: Understanding Webhook Security](#step-4-understanding-webhook-security)
    - [Verification Requests](#verification-requests)
    - [Validating Verification Requests](#validating-verification-requests)
    - [Validating Payloads](#validating-payloads)
  - [Step 5: Learn about the API and Build Your App](#step-5-learn-about-the-api-and-build-your-app)
  - [Step 6: Integrate AI into the Application](#step-6-integrate-ai-into-the-application)
  - [Step 7: Add a Phone Number](#step-7-add-a-phone-number)

## Get Started

1. **Overview & Setup**: Begin your journey [here](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started).
2. **Locate Your Bots**: Your bots can be found [here](https://developers.facebook.com/apps/).
3. **WhatsApp API Documentation**: Familiarize yourself with the [official documentation](https://developers.facebook.com/docs/whatsapp).
4. **Helpful Guide**: Here's a [Python-based guide](https://developers.facebook.com/blog/post/2022/10/24/sending-messages-with-whatsapp-in-your-python-applications/) for sending messages.
5. **API Docs for Sending Messages**: Check out [this documentation](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-messages).

## Step 1: Select Phone Numbers

- Make sure WhatsApp is added to your App.
- You begin with a test number that you can use to send messages to up to 5 numbers.
- Go to API Setup and locate the test number from which you will be sending messages.
- Here, you can also add numbers to send messages to. Enter your **own WhatsApp number**.
- You will receive a code on your phone via WhatsApp to verify your number.

## Step 2: Send Messages with the API

1. Obtain a 24-hour access token from the API access section.
2. It will show an example of how to send messages using a `curl` command which can be send from the terminal or with a tool like Postman.
3. Let's convert that into a [Python function with the request library](https://github.com/daveebbelaar/python-whatsapp-bot/blob/main/start/whatsapp_quickstart.py).
4. Create a `.env` files based on `example.env` and update the required variables.
5. You will receive a "Hello World" message (Expect a 60-120 second delay for the message).

Creating an access that works longer then 24 hours

1. Create a [system user at the Meta Business account level](https://business.facebook.com/settings/system-users).
2. On the System Users page, configure the assets for your System User, assigning your WhatsApp app with full control. Don't forget to click the Save Changes button.
   - [See step 1 here](https://github.com/daveebbelaar/python-whatsapp-bot/blob/main/img/meta-business-system-user-token.png)
   - [See step 2 here](https://github.com/daveebbelaar/python-whatsapp-bot/blob/main/img/adding-assets-to-system-user.png)
3. Now click `Generate new token` and select the app, and then choose how long the access token will be valid. You can choose 60 days or never expire.
4. Select all the permissions, as I was running into errors when I only selected the WhatsApp ones.
5. Confirm and copy the access token.

Now we have to find the following information on the **App Dashboard**:

- **APP_ID**: "<YOUR-WHATSAPP-BUSINESS-APP_ID>" (Found at App Dashboard)
- **APP_SECRET**: "<YOUR-WHATSAPP-BUSINESS-APP_SECRET>" (Found at App Dashboard)
- **RECIPIENT_WAID**: "<YOUR-RECIPIENT-TEST-PHONE-NUMBER>" (This is your WhatsApp ID, i.e., phone number. Make sure it is added to the account as shown in the example test message.)
- **VERSION**: "v18.0" (The latest version of the Meta Graph API)
- **ACCESS_TOKEN**: "<YOUR-SYSTEM-USER-ACCESS-TOKEN>" (Created in the previous step)

> You can only send a template type message as your first message to a user. That's why you have to send a reply first before we continue.

# Deploy Your Slack AI Bot to Azure

## 1. Introduction

In this section we'll deploy a Python-based WhatsApp bot to an Azure Web App! By deploying the bot to the cloud using Azure we'll allow it to be accessible from anywhere. Although we are using Azure in this repository, you can achieve similar results using other cloud platforms, such as AWS or Google Cloud Platform.

## 2. Azure Setup

In this section, we will guide you through setting up an Azure account and deploying a web app using the Deployment Center. Azure provides a comprehensive platform for deploying and managing your applications in the cloud.

Follow these steps to set up your Azure account and deploy your Slack bot:

1. **Sign up for an Azure account**: If you don't already have an account, sign up for a free Azure account at https://azure.microsoft.com. New users are eligible for a $200 credit, which you can use to explore and experiment with Azure services.

2. **Create a Resource Group**: A resource group helps you organize and manage resources based on their lifecycle and their relationship to each other. In the Azure Portal, create a new resource group called `Deploy-Whatsapp-Bot`.

3. **Create an App Service**: An App Service is a fully managed platform for building, deploying, and scaling your web apps. In the Azure Portal, create a new App Service and associate it with the `Deploy-Whatsapp-Bot` resource group. Set publish to `Code`, and select the correct `Python` version and your `Region` (There is a new region called 'Mexico central' which we will use). Finally, select an appropriate App Service Plan based on your needs. There is a free plan available.

4. **Deploy via GitHub repo**: In the Azure Deployment Center, connect your GitHub repository to your App Service. This will enable continuous integration and deployment, so your app will be automatically updated whenever you push changes to the specified branch. Make sure to select the correct branch.

Once you've completed these steps, your Azure account will be set up and ready for deploying your WhatsApp bot. In the next sections, we will discuss how to update the workflow file, the Python file, and the WhatsApp API connection to complete the deployment process.

### 2.1 Update the Startup Command in Azure

In the Azure portal, navigate to your App Service, and then go to Configuration > General Settings. Under the "Startup command" field, enter the following command and click "Save" to apply the changes.

```
startup.txt
```

### 2.2 Update the Web App Configuration with Keys and Secrets

In the Azure portal, navigate to your App Service, and then go to Configuration > Application settings. Add the following keys and their respective values. Make sure to replace the placeholder values with your actual keys and secrets. Click "Save" to apply the changes.

- `OPENAI_API_KEY`: Your OpenAI API key
- `ACCESS_TOKEN`: Key value
- `APP_SECRET`: Key value
- `APP_ID`: Key value
- `RECIPIENT_WAID`: Key value
- `VERSION`: Key value
- `PHONE_NUMBER_ID`: Key value
- `VERIFY_TOKEN`: Key value

## 3. Updating the Workflow File

In this section, we'll go over updating the GitHub Actions workflow file to enable automated deployments to your Azure App Service. We'll configure the workflow to log in to Azure CLI using a service principal and update the Azure credentials in GitHub Actions secrets.

Follow these steps to update the workflow file:

1. **Log in to Azure CLI using service principal**: In your GitHub Actions workflow file, add the following code snippet to enable logging in to the Azure CLI using a service principal:

```yml
- name: Log in to Azure CLI using service principal
  uses: azure/login@v1
  with:
    creds: ${{ secrets.AZURE_CREDENTIALS }}
```

2. **Create the service principal**: To create a service principal, run the following command in the Azure Cloud Shell, replacing `<YOUR-SUBSCRIPTION-ID>` with your actual subscription ID (Home > Subscriptions). This command will output a JSON object containing the necessary credentials, such as `clientId`, `clientSecret`, `subscriptionId`, and `tenantId`.

```bash
az ad sp create-for-rbac --name "myWhatsAppBotApp" --role contributor --scopes /subscriptions/<YOUR-SUBSCRIPTION-ID> --sdk-auth
```

3. **Update Azure credentials in GitHub Actions secrets**: In your GitHub repository, navigate to the "Settings" tab and then click on "Secrets and variables > Actions" in the left sidebar. Create a new repository secret named `AZURE_CREDENTIALS` and paste the JSON object you obtained in the previous step as its value.

With these updates in place, your GitHub Actions workflow is now configured to automatically deploy your WhatsApp bot to Azure whenever you push changes to the specified branch. In the next sections, we will discuss updating the Python file and the WhatsApp API connection.

## Step 3: Configure Webhooks to Receive Messages

#### Integrate WhatsApp

In the Meta App Dashboard, go to WhatsApp > Configuration, then click the Edit button.

1. In the Edit webhook's callback URL popup, enter the URL provided by the ngrok agent to expose your application to the internet in the Callback URL field, with /webhook at the end (i.e. https://<your-web-app>.azurewebsites.net/webhook).
2. Enter a verification token. This string is set up by you when you create your webhook endpoint. You can pick any string you like. Make sure to update this in your `VERIFY_TOKEN` environment variable.
3. After you add a webhook to WhatsApp, WhatsApp will submit a validation post request to your application. Confirm your localhost app receives the validation get request and logs `WEBHOOK_VERIFIED` in the terminal.
4. Back to the Configuration page, click Manage.
5. On the Webhook fields popup, click Subscribe to the **messages** field. Tip: You can subscribe to multiple fields.
6. If your Flask app and Azure Web App are running, you can click on "Test" next to messages to test the subscription. If you recieve a message your webhook is set up correctly.

#### Testing the Integration

First text the phone number that sent you the 'Quick Start, Hello World' Message template.

1. Add this number to your WhatsApp app contacts and then send a message to this number.
2. Confirm your localhost app receives a message and logs both headers and body in the terminal.
3. Test if the bot replies back to you.
4. You have now succesfully integrated the bot! 🎉

## Step 4: Understanding Webhook Security

#### Verification Requests

[Source](https://developers.facebook.com/docs/graph-api/webhooks/getting-started#:~:text=process%20these%20requests.-,Verification%20Requests,-Anytime%20you%20configure)

Anytime you configure the Webhooks product in your App Dashboard, we'll send a GET request to your endpoint URL. Verification requests include the following query string parameters, appended to the end of your endpoint URL. They will look something like this:

```
GET https://www.your-clever-domain-name.com/webhook?
  hub.mode=subscribe&
  hub.challenge=1158201444&
  hub.verify_token=12345
```

The verify_token, `12345` in the case of this example, is a string that you can pick. It doesn't matter what it is as long as you store in the `VERIFY_TOKEN` environment variable.

#### Validating Verification Requests

[Source](https://developers.facebook.com/docs/graph-api/webhooks/getting-started#:~:text=Validating%20Verification%20Requests)

Whenever your endpoint receives a verification request, it must:

- Verify that the hub.verify_token value matches the string you set in the Verify Token field when you configure the Webhooks product in your App Dashboard (you haven't set up this token string yet).

## Step 5: Learn about the API and Develop the App

Review the developer documentation to learn how to build the app and start sending messages. [See documentation](https://developers.facebook.com/docs/whatsapp/cloud-api).
