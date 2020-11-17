import { Observable, defer, from } from "rxjs";

const ROOT_URL = "http://127.0.0.1:8000";

export const fetchConversations = (): Observable<Conversation[]> => {
  return defer(() => {
    return from<Promise<Conversation[]>>(
      fetch(`${ROOT_URL}/conversations/`)
        .then((res) => res.json())
        .then(mapToConversations),
    );
  });
};
