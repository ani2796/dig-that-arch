import java.net.URI;
import java.net.URISyntaxException;
import java.util.Map;
import org.java_websocket.client.WebSocketClient;
import org.java_websocket.drafts.Draft;
import org.java_websocket.handshake.ServerHandshake;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

public class DetectorClient  extends WebSocketClient{
	
	// Some constants
	public static String hostName = "127.0.0.1";
	public static int port = 8081;
	public static String clientName = "JavaClient";
	public static String stage = "params";
	public static long round;
	public static long n, k, p;
	
	public DetectorClient(URI serverUri, Draft draft) {
		super(serverUri, draft);
	}
	
	public DetectorClient(URI serverURI) {
		super(serverURI);
	}
	
	public DetectorClient(URI serverUri, Map<String, String> httpHeaders) {
		super(serverUri, httpHeaders);
	}
	
	 @Override
	 public void onOpen(ServerHandshake handshakedata) {
		JSONObject obj = new JSONObject();
		obj.put("role", "Detector");
		obj.put("name", clientName);
		send(obj.toJSONString());
		System.out.println("opened connection");
		System.out.println("This is after opening the connection");
	}
	
	@Override
	public void onMessage(String message)  {
		System.out.println("received: " + message);
		JSONObject obj = null;
		try {
			obj = (JSONObject) new JSONParser().parse(message);
		} catch (ParseException e) {
			e.printStackTrace();
		}
		if(stage == "params") {
			System.out.println("Parameters obtained: n - " + obj.get("n") + " k - " + obj.get("k") + " p - " + obj.get("p"));
			n = (long)obj.get("n");
			k = (long)obj.get("k");
			p = (long)obj.get("p");
			
			stage = "detecting";
			return;
		} else if(stage == "detecting") {
			// Place your code here
			if(obj.keySet().contains("round")) {
				round = (long)obj.get("round");
				System.out.println("Round number: " + round);
				try {
					if(round <= n) {
						JSONObject retVal = (JSONObject)new JSONParser().parse("{\"name\": \"" + clientName + "\", \"vertices\": [[1, 1], [2, 3]], \"edges\": [[[0, 0], [0, 1]], [[1, 2], [2, 2]], [[2, 2], [3, 2]], [[2, 2], [2, 3]]]}");
						send(retVal.toJSONString());
					}
				} catch (ParseException e) {
					e.printStackTrace();
				}
			}
			else if(obj.keySet().contains("correct_edges") && obj.keySet().contains("correct_vertices")) {
				System.out.println("Receiving reply from server...");
				System.out.println("Correct edges: " + obj.get("correct_edges").toString());
				System.out.println("Correct vertices: " + obj.get("correct_vertices").toString());
				if(round == n) stage = "final";
			}
		} 
		if(stage == "final") {
			JSONObject finalGuess;
			try {
				finalGuess = (JSONObject) new JSONParser().parse("{\"edges\": [[[0, 0], [0, 1]], [[0, 1], [1, 1]], [[1, 1], [1, 2]], [[1, 2], [2, 2]], [[2, 2], [2, 3]]]}");
				send(finalGuess.toJSONString());
			} catch (ParseException e) {
				e.printStackTrace();
			}
		}
	}

	@Override
	public void onClose(int code, String reason, boolean remote) {
		System.out.println("Connection closed by " + (remote ? "remote peer" : "us") + " Code: " + code + " Reason: " + reason);
	}

	@Override
	public void onError(Exception ex) {
		ex.printStackTrace();
	}
	
	public static void main(String[] args) throws URISyntaxException {
		DetectorClient c = new DetectorClient(new URI(
	        "ws://" + hostName + ":" + port));
	    c.connect();
	  }
}
