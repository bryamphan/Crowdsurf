// Room page, shown at /room/:roomId. This is where guests spend the party.
//
// Placeholder for now. When built, it will:
//   - search songs (GET /tracks/search) and add them (POST /rooms/{id}/queue)
//   - show the ranked queue (GET /rooms/{id}/queue)
//   - let guests vote (PUT /rooms/{id}/queue/{itemId}/vote)
//   - update live as others vote (WebSocket /rooms/{id}/stream)

import { useParams } from "react-router-dom";

export default function Room() {
  const { roomId } = useParams();
  return (
    <main>
      <h1>Room {roomId}</h1>
      <p>Search, queue, and voting go here.</p>
    </main>
  );
}
