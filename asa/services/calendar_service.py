'''
 Calendar service class for interacting with user's calendars
 Exposes google calendar functions to provide calendar functionality for Asa.
'''

import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth.google_auth import get_google_credentials 


class CalendarService:
    def __init__(self):
      self.creds = get_google_credentials()
      self.service = build("calendar", "v3", credentials = self.creds)

    # get the user's calendar, the default is the user's primary calendar
    def get_user_calendar(name = "primary"):
        pass

    def get_upcoming_events(self, calendar_id="primary", max_results=10):
        """
         Retrieve the next set of upcoming events from the specified calendar.
        """
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            events_result = (
                self.service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=now,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            return events_result.get("items", [])
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

# holds the relevant calendar information for Asa
class Calendar:
    pass

