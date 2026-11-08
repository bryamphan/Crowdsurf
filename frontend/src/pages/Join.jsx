// Join page, shown at /join/:code. Guests land here after scanning the QR code.
//
// Placeholder for now. When built, it will:
//   - read the join code from the URL (useParams)
//   - let the guest pick a nickname and call POST /rooms/{code}/join
//   - save the guest token it gets back and send the guest to /room/:roomId

import { useParams } from "react-router-dom";

export default function Join() {
  const { code } = useParams();
  return (
    <main>
      <h1>Join room {code}</h1>
      <p>Nickname form goes here.</p>
    </main>
  );
}
