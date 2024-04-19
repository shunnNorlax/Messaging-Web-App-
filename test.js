// Function to generate asymmetric key pair from a password
async function generateKeyPairFromPassword(password) {
    // Convert the password to a key using PBKDF2
    const passwordBuffer = new TextEncoder().encode(password);
    const keyMaterial = await window.crypto.subtle.importKey(
      "raw",
      passwordBuffer,
      { name: "PBKDF2" },
      false,
      ["deriveBits", "deriveKey"]
    );
  
    // Derive a key from the password using PBKDF2
    const salt = new Uint8Array(16); // Salt
    const iterations = 100000; // Number of iterations
    const keyLength = 256; // Key length
    const derivedBits = await window.crypto.subtle.deriveBits(
      {
        name: "PBKDF2",
        salt: salt,
        iterations: iterations,
        hash: "SHA-256"
      },
      keyMaterial,
      keyLength
    );
  
    // Use the derived bits to generate an asymmetric key pair
    const keyPair = await window.crypto.subtle.generateKey(
      {
        name: "RSA-OAEP",
        modulusLength: 2048,
        publicExponent: new Uint8Array([0x01, 0x00, 0x01]), // 65537
        hash: "SHA-256"
      },
      true,
      ["encrypt", "decrypt"]
    );
  
    return keyPair;
  }
  
  // Example usage
  async function example() {
    const password = "yourPassword";
    
    try {
      // Generate key pair
      const keyPair = await generateKeyPairFromPassword(password);
      console.log("Private Key:", keyPair.privateKey);
      console.log("Public Key:", keyPair.publicKey);
    } catch (error) {
      console.error("Error:", error);
    }
  }
  
  example();
  
  // Function to encrypt data using the public key
async function encryptData(data, publicKey) {
    const encodedData = new TextEncoder().encode(data);
    const encryptedData = await window.crypto.subtle.encrypt(
      {
        name: "RSA-OAEP"
      },
      publicKey,
      encodedData
    );
    return encryptedData;
  }
  
  // Function to decrypt data using the private key
  async function decryptData(encryptedData, privateKey) {
    const decryptedData = await window.crypto.subtle.decrypt(
      {
        name: "RSA-OAEP"
      },
      privateKey,
      encryptedData
    );
    const decodedData = new TextDecoder().decode(decryptedData);
    return decodedData;
  }
  
  // Example usage
  async function example() {
    const password = "yourPassword";
    const dataToEncrypt = "Hello, world!";
    
    try {
      // Generate key pair
      const keyPair = await generateKeyPairFromPassword(password);
      
      // Encrypt data
      const encryptedData = await encryptData(dataToEncrypt, keyPair.publicKey);
      console.log("Encrypted Data:", new Uint8Array(encryptedData));
  
      // Decrypt data
      const decryptedData = await decryptData(encryptedData, keyPair.privateKey);
      console.log("Decrypted Data:", decryptedData);
    } catch (error) {
      console.error("Error:", error);
    }
  }
  
  example();
  