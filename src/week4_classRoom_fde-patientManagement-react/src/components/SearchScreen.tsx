import type { encounterInterface } from "../types";

interface SearchScreenProps {
     encounter: encounterInterface;
}
//search screen to display patient number as text field , risk level as dropdown and risk score as text fields with a search button
//on clicking search button, the search results should be displayed in a table below the search form. The table should display the encounter id, patient number, risk level, risk score and age of the patient. The table should also have a pagination component to navigate through the pages of encounter data. 
// The current page and total pages should be tracked in the state, and the onPageChange function should update the current page when the user clicks on the pagination buttons. Maximum of 40 encounters should be displayed per page.
export default function SearchScreen({ encounter }: SearchScreenProps) {
    return (
        <div>
            <h2>Search Screen</h2>
            <form>
                <label htmlFor="patient_nbr">Patient Number:</label>
                <input type="text" id="patient_nbr" name="patient_nbr" />
                <label htmlFor="risk_level">Risk Level:</label>
                <select id="risk_level" name="risk_level">
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HIGH">HIGH</option>
                </select>
                <label htmlFor="risk_score">Risk Score:</label>
                <input type="text" id="risk_score" name="risk_score" />
                <button type="submit">Search</button>
            </form>
        </div>
    );
}