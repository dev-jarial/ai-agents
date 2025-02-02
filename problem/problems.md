I have to build the agentic ai which can handle the customer support for voltas AC company agent can user the Number like +91 9876543210 and dummy database which is in the form of the json file to valid the user and his purchase. When user send query like:

User: I have bought voltas AC 6 months ago, but it is not working properly. Can you please register my complaint.

backend process: agent check if the conversation on going or just start. If just start then will send the greeting message or apologies or may be sympathy response as per user query.
like in this user query.

agent: Apologies for the inconvenience, can you please confirm your email Id and registered mobile number to register your complaint.

User: My number is 12532t3262 and email is pankaj@gmail.com

backend process: agent check the database or api call (for current system we can use the json demo data ) if user is verified, then proceed with the next steup like asking about the model number or invoice copy of the product. 
other-wise gave 3 fall back tries then ask user to contact with the customer service agents if User want and if he said yes then share the number with him
check cases:

    if verification failed for 1st time:

        agent (fall back 1 message): Sorry, this is not registered mobile number or email, can please share registered number or email ID, to register your complaint.
    
    elif verification failed for 2nd time:
        agent (fall back 2 message): Sorry, this is not registered mobile number or email, can please share registered number or email ID, to register your complaint.
    
    elif verification failed for 3rd time:
        agent (fall back 2 message): Sorry, again this is not registered mobile number or email, do you want to contact with the customer suppport agent
            
        User: Yes or No

        if yes:
            share the number with the User
        else No:
            send the message to like, thanks for reaching us.
    
    else verification successful:
        ask for the model number or invoice (we can check the dummy json data if the model is present and warranty is existed like purchase was 6  months ago. As warranty can be valid for one year.)
        
        if valid:
            then ask for issue User facing with the AC.
            
            User: Issue in the colling
            Backend Process: register the complaint and generate the ticket then send it to user.

        else:
            Tell the user that warrantly is expired.
            user: insiting for the issue, like warrantly must be valid
            agent: ask him, if User would like to talk with the customer service agent.
            User: Yes or no
            if yes:
                share the Number with the user.
            else:
                send the thanks for visiting message.




Problem: 2


suggestions an AC for a room, recently married.

Would you like to help me to find out the best model.

L*W = 30"40"

promotion available.
split AC or window AC or both?


If selection is done:
check fall back message: discount or recommendation.

Problem: 3

lead generation.

search internet based on the user query or thought. (SDR)
Schedule call through email. ( ask for date to schedule the meeting )
fall back message: for more detailing regarding the products.