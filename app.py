from flask import Flask, render_template, request, redirect, flash
import firebase_admin,json
from firebase_admin import credentials,storage
import webbrowser
from setup import *
import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = "super secret key"

cred = credentials.Certificate("config.json")
firebase_admin.initialize_app(cred ,{
    'storageBucket': 'cloudstorageverifier.appspot.com'
})


mainStorage = storage.bucket()
blob = mainStorage.blob("loginInfo.json")
blob.download_to_filename("loginInfo.json")
loginInfo = json.load(open("loginInfo.json"))

app.config['UPLOAD_FOLDER'] = ""
app.config['UPLOAD_FOLDER'] = 1024

contract,web3 = setup()

USER_ID = None



@app.route("/")
def show_home():
    return render_template('home.html')



@app.route("/Login",methods = ['POST'])
def Login():
    if request.method == 'POST':
        if request.form:
            uid = request.form["user_id"]
            password = request.form["pass"]
            if uid in loginInfo and loginInfo[uid] == password:
                global USER_ID
                USER_ID= uid
                flash("Logged In, Successfully!")
                return redirect("/FileManager")
            else:
                flash("Wrong User Id or Password!")

    return render_template("home.html")

@app.route("/logout")
def logout():
    global USER_ID
    USER_ID = None
    flash("Successfully Logged Out!")
    return redirect("/")

@app.route("/SignUp")
def showSignUp():
    return render_template("newUser.html")

@app.route("/register",methods=['POST'])
def SignUp():
    if request.method == 'POST':
        if request.form:
            uid = request.form["user_id"]
            password = request.form["pass"]
            if uid in loginInfo:
                flash("Not a valid user!")
            else:
                loginInfo[uid] = password
                with open("loginInfo.json", "w") as outfile:
                    json.dump(loginInfo, outfile)
                blob = mainStorage.blob("loginInfo.json")
                blob.upload_from_filename("loginInfo.json")
                return redirect("/")

    return render_template("newUser.html")


@app.route("/FileManager")
def FileManager():
    if USER_ID != None:
        files = []
        bucket = storage.bucket()
        blobs = list(bucket.list_blobs())
        for i in blobs:
            if "fileManager/" in i.name and i.name.replace("fileManager/","") != "":
                file = []
                file.append(i.name.replace("fileManager/",""))
                file.append("."+file[0].split(".")[1])
                file.append(i.public_url)
                files.append(file)

        return render_template("FileManager.html",values=files)
    else:
        return redirect("/")

@app.route("/delete/<file>")
def deleteFile(file):
    bucket = storage.bucket()
    bucket.delete_blob("fileManager/"+file)

    # Send Command to Block Chain!
    tx_info = contract.functions.build(str(USER_ID) + " Deleted a file named : " + file,
                                       str(datetime.datetime.now()), str(USER_ID), file).transact()
    tx_info = web3.eth.waitForTransactionReceipt(tx_info)
    print("Transaction Successful with id : " + str(tx_info["transactionHash"]))

    flash("File Deleted Successfully")
    return redirect("/FileManager")

@app.route("/upload_file",methods=["POST"])
def uploadFile():
    if request.method == "POST":
        if request.files:
            f = request.files['file']
            f.filename = "fileManager/" + f.filename
            bucket = storage.bucket()
            blob = bucket.blob(f.filename)

            # Send to blockchain
            tx_info = contract.functions.build(str(USER_ID)+" Uploaded a file named : "+f.filename[12:],str(datetime.datetime.now()),str(USER_ID),f.filename[12:]).transact()
            tx_info = web3.eth.waitForTransactionReceipt(tx_info)
            print("Transaction Successful with id : " + str(tx_info["transactionHash"]))

            blob.upload_from_file(f)
            blob.make_public()
            flash("File Uploaded Successfully")
    return redirect("/FileManager")

@app.route("/download/<ind>")
def downloadFile(ind):
    files = []
    bucket = storage.bucket()
    blobs = list(bucket.list_blobs())
    for i in blobs:
        if "fileManager/" in i.name and i.name.replace("fileManager/", "") != "":
            file = []
            file.append(i.name.replace("fileManager/", ""))
            file.append("." + file[0].split(".")[1])
            file.append(i.public_url)
            files.append(file)

    # send message
    tx_info = contract.functions.build(str(USER_ID) + " Downloaded a file named : " + files[int(ind) - 1][0],
                                       str(datetime.datetime.now()), str(USER_ID), files[int(ind) - 1][0]).transact()
    tx_info = web3.eth.waitForTransactionReceipt(tx_info)
    print("Transaction Successful with id : " + str(tx_info["transactionHash"]))

    flash("File Downloaded Successfully")
    webbrowser.open(files[int(ind) - 1][2])
    return redirect("/FileManager")

@app.route("/ActivityLog")
def ActivityLog():
    if USER_ID != None:
        activities = []
        for i in range(0,contract.functions.count().call()):
                activity = []
                activity.append(contract.functions.file_name(i).call())
                activity.append(contract.functions.user_id(i).call())
                activity.append(contract.functions.log_data(i).call())
                activity.append(contract.functions.time_stamp(i).call())
                activities.append(activity)

        return render_template("ActivityLog.html",values=activities)
    else:
        return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

