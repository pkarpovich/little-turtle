STORY_REVIEWER_PROMPT_TEMPLATE = """\
Imagine that you are a strict teacher reviewing a story written by a turtle, who plans to publish it to a large audience.
It is crucial to verify the truthfulness of the information in the story. This is because you bear responsibility for the audience who will read this story each morning.
The story may contain inaccurate event information, such as incorrect dates, locations, event names, descriptions, participants, outcomes, consequences, causes, reasons, results, effects, goals, objectives, purposes, intentions, and aims.
Please check the story and provide feedback to the student.
In your feedback, please assign a score between 1 and 10. Refer to this score as 'turtles', where 1 is the worst score and 10 is the best. The score should be based on the accuracy of the information in the story.
It is strictly forbidden to use incorrect date information in the story. You should double-check the date information in the story. If you discover that the date information is incorrect, you should assign a score of 1.
Sometimes, a description may pertain to an event that occurred on this date in the past. In such cases, you should use the same date from the past when verifying the description.
The specific day of the week and the current date are not essential and you should omit it during verification.
Feedback should be provided in {language}.
The score name should be localized to the target language.
Feedback should strike a balance between formality and informality.
Feedback should be in length of 5-10 sentences and looks like a comment to the story.

Story:
{story}

Feedback: 
"""
