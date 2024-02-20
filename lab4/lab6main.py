from flask import Flask, render_template, request, redirect, url_for
from ospfconfig import connectRouter, configureOSPFAndRedirect
from sshInfo import sshInfo
from getconfig import getRunningConfig
from diffconfig import diffConfig
from migration import mainMigration

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get-config")
def getConfig():
    return f"Saved the running-config of the routers. Here are the file names: \n{str(getRunningConfig())}"

@app.route("/ospf-config", methods=["GET", "POST"])
def ospfConfig():
    routers = ["R1", "R2", "R3", "R4"]

    error_message = None

    router_index = int(request.args.get("router_index", 0))
    router = routers[router_index]

    if request.method == "POST":
        username = request.form.get(f"{router}_username")
        password = request.form.get(f"{router}_password")
        router_ip = sshInfo()[router]["IP"]
        device_type = 'ios'
        ospfprocess = request.form.get(f"{router}_ospfprocess")
        loopbackip = request.form.get(f"{router}_loopback")
        ospfadvertise = request.form.get(f"{router}_advertise").split()        

        loopback0_ip, device = connectRouter(device_type, router_ip, username, password)

        success, error_message, next_router_index = configureOSPFAndRedirect(router_index, routers, router, loopbackip, loopback0_ip, device, ospfprocess, ospfadvertise)
        if success:
            if next_router_index is not None:
                return redirect(url_for("ospfConfig", router_index=next_router_index))
            else:
                return error_message
        else:
            return render_template("ospfconfig.html", router=router, error_message=error_message)

    return render_template("ospfconfig.html", router=router, error_message=error_message)

@app.route("/diff-config")
def displayDiff():
    diff = diffConfig()
    return f"Here's the diff for all routers:<br/>{diff}"

@app.route("/migration")
def migration():
    mainMigration()
    return "Migration completed successfully"

if __name__ == "__main__":
    app.debug = True
    app.run("127.0.0.1", port=80)