// SPDX-FileCopyrightText: 2026 AIFENCE contributors
// SPDX-License-Identifier: Apache-2.0
package aifence

import "testing"

func TestRejectsInsecureBaseURL(t *testing.T) {
	if _, err := NewClient("http://aifence.local", "key", nil); err == nil {
		t.Fatal("expected insecure URL to be rejected")
	}
}
