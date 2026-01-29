import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyC2R6xsjtVb0dckwouDXQsrT493-2n58v0",
  authDomain: "schema-intelligence-layer.firebaseapp.com",
  projectId: "schema-intelligence-layer",
  appId: "1:781806095541:web:2df4e6363b84bf862382fc",
};
const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
