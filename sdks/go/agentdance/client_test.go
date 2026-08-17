// SPDX-FileCopyrightText: 2026 AGENTDANCE contributors
// SPDX-License-Identifier: Apache-2.0
package agentdance

import "testing"

func TestRejectsInsecureBaseURL(t *testing.T) {
	if _, err := NewClient("http://agentdance.local", "key", nil); err == nil {
		t.Fatal("expected insecure URL to be rejected")
	}
}
