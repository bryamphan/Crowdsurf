// Host page, shown at / and /host on the host's TV or laptop.
//
// Placeholder for now. When built, it will:
//   - create a room (POST /rooms)
//   - show a QR code that links guests to /join/{code}
//   - play the song at the top of the queue and advance with POST /rooms/{id}/next
//   - update live as guests vote (WebSocket /rooms/{id}/stream)
export default function Host() {
  return (
    <main>
      <h1>Crowdsurf</h1>
      <p>Host view. Create a room and show the QR code here.</p>
    </main>
  );
}
