from main import app
import os
if __name__ == "__main__":
    port_no = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port_no)