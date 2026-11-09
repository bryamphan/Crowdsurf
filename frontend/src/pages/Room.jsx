// Room page, shown at /room/:roomId. This is where guests spend the party.

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
