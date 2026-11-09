// Join page, shown at /join/:code. Guests land here after scanning the QR code.

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
