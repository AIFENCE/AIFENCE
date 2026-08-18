package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"math"
	"os"
	"regexp"
	"sort"
	"strconv"
	"strings"
)

type vectors struct {
	Valid   []vector `json:"valid"`
	Invalid []vector `json:"invalid"`
}

type vector struct {
	Name             string         `json:"name"`
	Wire             map[string]any `json:"wire"`
	CanonicalJSON    string         `json:"canonical_json"`
	CanonicalMsgpack string         `json:"canonical_msgpack_hex"`
	CanonicalSHA     string         `json:"canonical_sha256"`
}

func prefix(code byte, value uint64, n int) []byte {
	out := make([]byte, 1+n)
	out[0] = code
	switch n {
	case 1:
		out[1] = byte(value)
	case 2:
		binary.BigEndian.PutUint16(out[1:], uint16(value))
	case 4:
		binary.BigEndian.PutUint32(out[1:], uint32(value))
	case 8:
		binary.BigEndian.PutUint64(out[1:], value)
	}
	return out
}

func encInt(v int64) []byte {
	if v >= 0 {
		u := uint64(v)
		if u <= 0x7f {
			return []byte{byte(u)}
		}
		if u <= 0xff {
			return prefix(0xcc, u, 1)
		}
		if u <= 0xffff {
			return prefix(0xcd, u, 2)
		}
		if u <= 0xffffffff {
			return prefix(0xce, u, 4)
		}
		return prefix(0xcf, u, 8)
	}
	if v >= -32 {
		return []byte{byte(256 + v)}
	}
	if v >= -128 {
		return []byte{0xd0, byte(int8(v))}
	}
	if v >= -32768 {
		out := []byte{0xd1, 0, 0}
		binary.BigEndian.PutUint16(out[1:], uint16(int16(v)))
		return out
	}
	if v >= -2147483648 {
		out := make([]byte, 5)
		out[0] = 0xd2
		binary.BigEndian.PutUint32(out[1:], uint32(int32(v)))
		return out
	}
	return prefix(0xd3, uint64(v), 8)
}

func encString(s string) []byte {
	b := []byte(s)
	var h []byte
	n := len(b)
	if n <= 31 {
		h = []byte{byte(0xa0 | n)}
	} else if n <= 0xff {
		h = prefix(0xd9, uint64(n), 1)
	} else if n <= 0xffff {
		h = prefix(0xda, uint64(n), 2)
	} else {
		h = prefix(0xdb, uint64(n), 4)
	}
	return append(h, b...)
}

func encode(v any) ([]byte, error) {
	switch x := v.(type) {
	case nil:
		return []byte{0xc0}, nil
	case bool:
		if x {
			return []byte{0xc3}, nil
		}
		return []byte{0xc2}, nil
	case string:
		return encString(x), nil
	case json.Number:
		if !strings.ContainsAny(string(x), ".eE") {
			if i, e := x.Int64(); e == nil {
				return encInt(i), nil
			}
		}
		f, e := x.Float64()
		if e != nil || math.IsNaN(f) || math.IsInf(f, 0) {
			return nil, errors.New("invalid number")
		}
		out := make([]byte, 9)
		out[0] = 0xcb
		binary.BigEndian.PutUint64(out[1:], math.Float64bits(f))
		return out, nil
	case []any:
		n := len(x)
		var h []byte
		if n <= 15 {
			h = []byte{byte(0x90 | n)}
		} else if n <= 0xffff {
			h = prefix(0xdc, uint64(n), 2)
		} else {
			h = prefix(0xdd, uint64(n), 4)
		}
		out := bytes.NewBuffer(h)
		for _, item := range x {
			b, e := encode(item)
			if e != nil {
				return nil, e
			}
			out.Write(b)
		}
		return out.Bytes(), nil
	case map[string]any:
		keys := make([]string, 0, len(x))
		for k := range x {
			keys = append(keys, k)
		}
		sort.Strings(keys)
		n := len(keys)
		var h []byte
		if n <= 15 {
			h = []byte{byte(0x80 | n)}
		} else if n <= 0xffff {
			h = prefix(0xde, uint64(n), 2)
		} else {
			h = prefix(0xdf, uint64(n), 4)
		}
		out := bytes.NewBuffer(h)
		for _, k := range keys {
			out.Write(encString(k))
			b, e := encode(x[k])
			if e != nil {
				return nil, e
			}
			out.Write(b)
		}
		return out.Bytes(), nil
	default:
		return nil, fmt.Errorf("unsupported type %T", v)
	}
}

func canonicalJSON(v any) ([]byte, error) { return json.Marshal(v) }

var traceRe = regexp.MustCompile(`^[0-9a-f]{2}-[0-9a-f]{32}-[0-9a-f]{16}-[0-9a-f]{2}$`)

func validate(w map[string]any) error {
	allowed := map[string]bool{"v": true, "c": true, "a": true, "i": true, "s": true, "r": true, "x": true, "R": true, "b": true, "d": true, "p": true, "m": true, "g": true, "z": true}
	for k := range w {
		if !allowed[k] {
			return fmt.Errorf("unknown top-level key %s", k)
		}
	}
	vn, ok := w["v"].(json.Number)
	if !ok || string(vn) != "2" {
		return errors.New("wire version")
	}
	if _, ok := w["c"].(string); !ok {
		return errors.New("codebook")
	}
	if p, ok := w["p"].(map[string]any); ok {
		if q, exists := p["q"]; exists {
			n, ok := q.(json.Number)
			if !ok {
				return errors.New("provenance confidence")
			}
			f, _ := n.Float64()
			if f < 0 || f > 1 {
				return errors.New("provenance confidence")
			}
		}
	}
	if raw, exists := w["x"]; exists {
		arr, ok := raw.([]any)
		if !ok {
			return errors.New("atoms")
		}
		atomAllowed := map[string]bool{"c": true, "v": true, "l": true, "h": true, "p": true, "q": true, "e": true}
		for _, a := range arr {
			m, ok := a.(map[string]any)
			if !ok {
				return errors.New("atom")
			}
			for k := range m {
				if !atomAllowed[k] {
					return errors.New("unknown atom key")
				}
			}
			if q, exists := m["q"]; exists {
				n, ok := q.(json.Number)
				if !ok {
					return errors.New("atom confidence")
				}
				f, _ := n.Float64()
				if f < 0 || f > 1 {
					return errors.New("atom confidence")
				}
			}
			if e, exists := m["e"]; exists {
				if _, ok := e.(string); !ok {
					return errors.New("epistemic type")
				}
			}
		}
	}
	if g, ok := w["g"].(map[string]any); ok {
		if g["alg"] != "Ed25519" {
			return errors.New("signature algorithm")
		}
	}
	if z, ok := w["z"].(map[string]any); ok {
		p, ok := z["p"].(string)
		if !ok || !traceRe.MatchString(p) {
			return errors.New("traceparent")
		}
		if s, exists := z["s"]; exists {
			if _, ok := s.(string); !ok {
				return errors.New("tracestate")
			}
		}
	}
	return nil
}

func main() {
	path := "tck/vectors/core.json"
	if len(os.Args) > 1 {
		path = os.Args[1]
	}
	data, err := os.ReadFile(path)
	if err != nil {
		panic(err)
	}
	dec := json.NewDecoder(bytes.NewReader(data))
	dec.UseNumber()
	var suite vectors
	if err := dec.Decode(&suite); err != nil {
		panic(err)
	}
	failures := []string{}
	total := 0
	for _, t := range suite.Valid {
		total++
		if err := validate(t.Wire); err != nil {
			failures = append(failures, t.Name+": "+err.Error())
			continue
		}
		cj, _ := canonicalJSON(t.Wire)
		packed, e := encode(t.Wire)
		if e != nil {
			failures = append(failures, t.Name+": "+e.Error())
			continue
		}
		sum := sha256.Sum256(packed)
		if t.CanonicalJSON != "" && string(cj) != t.CanonicalJSON {
			failures = append(failures, t.Name+": canonical JSON mismatch")
		}
		if hex.EncodeToString(packed) != t.CanonicalMsgpack {
			failures = append(failures, t.Name+": canonical MessagePack mismatch")
		}
		if "sha256:"+hex.EncodeToString(sum[:]) != t.CanonicalSHA {
			failures = append(failures, t.Name+": digest mismatch")
		}
	}
	for _, t := range suite.Invalid {
		total++
		if validate(t.Wire) == nil {
			failures = append(failures, t.Name+": invalid vector accepted")
		}
	}
	result := map[string]any{"ok": len(failures) == 0, "total": total, "passed": total - len(failures), "failures": failures}
	out, _ := json.Marshal(result)
	fmt.Println(string(out))
	if len(failures) > 0 {
		os.Exit(1)
	}
	_ = strconv.IntSize
}
