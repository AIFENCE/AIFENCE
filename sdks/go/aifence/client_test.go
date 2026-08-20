// SPDX-FileCopyrightText: 2026 AIFENCE contributors
// SPDX-License-Identifier: Apache-2.0
package aifence

import "testing"

func TestRejectsInsecureBaseURL(t *testing.T) {
	if _, err := NewClient("http://aifence.local", "key", nil); err == nil {
		t.Fatal("expected insecure URL to be rejected")
	}
}

func TestFenceURLResolvesOutsideGuardMount(t *testing.T) {
	client, err := NewClient("https://aifence.local/guard", "key", nil)
	if err != nil {
		t.Fatal(err)
	}
	if got, want := client.fenceURL.String(), "https://aifence.local/v1/fence/submit"; got != want {
		t.Fatalf("fence URL = %q, want %q", got, want)
	}
}
