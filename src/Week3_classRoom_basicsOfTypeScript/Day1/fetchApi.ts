async function getEncounterDetails(): Promise<any> {
    const response = await fetch('http://127.0.0.1:8001/encounters?limit=5');

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }

    console.log("Response from API:", response.status);
    const data = await response.json();
    console.log("Response from API:", data);
    return data;
}

getEncounterDetails();