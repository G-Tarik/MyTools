package main
import (
	"os"
	"fmt"
	"bufio"
	"math/big"
	"encoding/hex"
        "github.com/ethereum/go-ethereum/crypto"
        "github.com/ethereum/go-ethereum/crypto/sha3"
        "github.com/ethereum/go-ethereum/rlp"
        "github.com/ethereum/go-ethereum/core/types"
        "github.com/ethereum/go-ethereum/common"
        //"github.com/ethereum/go-ethereum/params"
)

const (
	// chainID is network ID
	CHAIN_ID = 1
)


func getPubKey(messageToSign,sig []byte) {
	pub, err_pub := crypto.SigToPub(messageToSign, sig)
	if err_pub != nil {fmt.Println("err_pub1: ",err_pub)}

	//pub1Bytes := crypto.FromECDSAPub(pub1)[1:]
	fmt.Printf("pubX:%d\npubY:%d\n", pub.X, pub.Y)
	addr := crypto.PubkeyToAddress(*pub).String()
	fmt.Printf("Address from signature:\n%v\n", addr[2:])
}


// make hash of the message to be signed
func rlpHash(x interface{}) (h common.Hash) {
        hw := sha3.NewKeccak256()
        rlp.Encode(hw, x)
        hw.Sum(h[:0])
        return h
}


// message to be signed
func getMessage(tx *types.Transaction) common.Hash {
	nonce := tx.Nonce()
	gasPrice := tx.GasPrice()
	gasLimit := tx.Gas()
	recipient := tx.To()
	value := tx.Value()
	input := []byte("")

	return rlpHash([]interface{}{
                nonce,
                gasPrice,
                gasLimit,
                recipient,
                value,
                input,
		//uncomment if transaction is not protected
                //big.NewInt(CHAIN_ID), uint(0), uint(0),
        })
}


func main() {
	var tx *types.Transaction
	scanner := bufio.NewScanner(os.Stdin)
	fmt.Println("Provide raw transaction:\n")
	scanner.Scan()
	data := scanner.Text()
	rawtx,_ := hex.DecodeString(data)
	rlp.DecodeBytes(rawtx, &tx)
	fmt.Println(tx)

	//signer := types.NewEIP155Signer(big.NewInt(CHAIN_ID))
	//signer := types.MakeSigner( params.MainnetChainConfig, big.NewInt(4989292) )
	//fromAddr, _ := signer.Sender(tx)
	//tx_to_sign := signer.Hash(tx)

	tx_to_sign := getMessage(tx)
	msg := tx_to_sign.Bytes()
	V,R,S := tx.RawSignatureValues()
	v := new(big.Int).Sub( V, big.NewInt(27) )

	sig,_ := hex.DecodeString( R.Text(16) + S.Text(16) + "0" + v.String() )
	getPubKey( msg, sig )
}
