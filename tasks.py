from crewai import Task

# Overview of task: Take data from CSV file. This data + template email will be turned into a personalized email by the agent doing the first task. 
# Then, this personalized email will be turned into a ghostwritten email to make it sound less botty, this done by second agent doing second task.
# Will be put in output folder.

class PersonalizeEmailTask():
    def personalize_email(self, agent, recipient, email_template): # pass all of info from csv file in recipient
        return Task(
            description=f"""
                Personalize the template email for recipient using their information.

                - Name: {recipient['first_name']} {recipient['last_name']}
                - Email: {recipient['email']}
                - Bio: {recipient['bio']}
                - Last conversation: {recipient['last_conversation']}

                Important Info to consider:
                - When personalizing the email, only use one sentence from the bio or last conversation. 
                    And make sure to incorporate it naturally into the email.  without going too much in to detail.
                - Make sure to keep the updated email roughly the same same length as the template email.
                
                The template email is as follows:

                ```
                {email_template}
                ```
            """,
            agent=agent,
            expected_output=f"Personalized email draft.",
            async_execution=True, # speeds up crew - allows the writing to be done simulteneous - beware of rate limits.
        )

    def ghostwrite_email(self, agent, draft_email, recipient):
        return Task(
            description=f"""
                Revise the draft email to adopt the following writing style.

                Writing Style:
                - Use a more informal, engaging, and slightly sales-oriented tone, mirroring ghost writer's final email communication style. 
                - This approach prioritizes clear, direct communication while maintaining a friendly and approachable tone. 
                - Use straightforward language, including phrases like "Hey [Name]!" to start emails or messages. 
                - The tone will be optimistic and encouraging, aiming to build rapport and motivate action, while staying grounded in practical advice.

                Important Notes:
                - Do not use emojis.
            """,
            agent=agent,
            context=[draft_email], # context requires a list - when you have other tasks pass their output for context for this task. Helpful for tasks in series.
            expected_output=f"A revised email draft in ghost writer's specified tone and style.",
            output_file=f"output/{recipient['first_name']}_{recipient['last_name']}.txt", # spits out everything into this output file.
        )
