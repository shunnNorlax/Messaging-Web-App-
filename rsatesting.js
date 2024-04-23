const NodeRSA = require('node-rsa');
function generateRSAkeyPair() {
    const key = new NodeRSA({ b: 1024 }); // You can adjust the key size as per your requirement
    return {
        public_key: key.exportKey('pkcs1-pem'), // Export public key as PEM format string
        private_key: key.exportKey('pkcs1-pem') // Export private key as PEM format string
    };
}

const keyPair = generateRSAkeyPair();
const publicKey = new NodeRSA(keyPair.public_key);
const privateKey = new NodeRSA(keyPair.private_key);

console.log("Public Key:", keyPair.public_key);
console.log("Private Key:", keyPair.public_key);

const msg = "hello";

var encryptMsg = publicKey.encrypt(msg, 'base64');// more readalbe not toolong string

var decryptMsg = privateKey.decrypt(encryptMsg, 'utf8' );

console.log(decryptMsg);