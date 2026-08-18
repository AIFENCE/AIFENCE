package sagewire

const Protocol = "sage/0.2"
const WireVersion = 2

type Packet map[string]any

var WireKeys = map[string]struct{}{
	"R": {},
	"a": {},
	"b": {},
	"c": {},
	"d": {},
	"g": {},
	"i": {},
	"m": {},
	"p": {},
	"r": {},
	"s": {},
	"v": {},
	"x": {},
	"z": {},
}
