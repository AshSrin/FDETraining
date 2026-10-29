from database import get_connection


#from table  review_periods create a function to get all review periods from the database
def get_all_review_periods():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM review_periods")
    review_periods = cursor.fetchall()
    cursor.close()
    connection.close()
    print(review_periods)
    return review_periods

