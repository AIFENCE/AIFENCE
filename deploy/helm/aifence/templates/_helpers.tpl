{{- define "aifence.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "aifence.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name (include "aifence.name" .) | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{- define "aifence.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "aifence.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "aifence.selectorLabels" -}}
app.kubernetes.io/name: {{ include "aifence.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "aifence.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "aifence.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}



{{- define "aifence.workerServiceAccountName" -}}
{{- if .Values.worker.serviceAccount.create }}
{{- default (printf "%s-dispatcher" (include "aifence.fullname" .)) .Values.worker.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.worker.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "aifence.lifecycleServiceAccountName" -}}
{{- if .Values.lifecycleWorker.serviceAccount.create }}
{{- default (printf "%s-lifecycle" (include "aifence.fullname" .)) .Values.lifecycleWorker.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.lifecycleWorker.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "aifence.anchorServiceAccountName" -}}
{{- if .Values.anchorWorker.serviceAccount.create }}
{{- default (printf "%s-anchor" (include "aifence.fullname" .)) .Values.anchorWorker.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.anchorWorker.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "aifence.image" -}}
{{- if and .Values.image.requireDigest (not .Values.image.digest) -}}
{{- fail "image.digest is required when image.requireDigest is true" -}}
{{- end -}}
{{- if .Values.image.digest -}}
{{- printf "%s@%s" .Values.image.repository .Values.image.digest -}}
{{- else -}}
{{- printf "%s:%s" .Values.image.repository .Values.image.tag -}}
{{- end -}}
{{- end }}

{{- define "aifence.clamavImage" -}}
{{- if .Values.clamav.image.digest -}}
{{- printf "%s@%s" .Values.clamav.image.repository .Values.clamav.image.digest -}}
{{- else -}}
{{- printf "%s:%s" .Values.clamav.image.repository .Values.clamav.image.tag -}}
{{- end -}}
{{- end }}

{{- define "aifence.dnsEgress" -}}
- to:
    - namespaceSelector:
        {{- toYaml .Values.networkPolicy.dns.namespaceSelector | nindent 8 }}
      podSelector:
        {{- toYaml .Values.networkPolicy.dns.podSelector | nindent 8 }}
  ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
{{- end }}

{{- define "aifence.databaseEgress" -}}
{{- if gt (len .Values.networkPolicy.database.namespaceSelector) 0 }}
- to:
    - namespaceSelector:
        {{- toYaml .Values.networkPolicy.database.namespaceSelector | nindent 8 }}
      {{- if gt (len .Values.networkPolicy.database.podSelector) 0 }}
      podSelector:
        {{- toYaml .Values.networkPolicy.database.podSelector | nindent 8 }}
      {{- end }}
  ports:
    - protocol: TCP
      port: {{ .Values.networkPolicy.database.port }}
{{- else if gt (len .Values.networkPolicy.database.podSelector) 0 }}
- to:
    - podSelector:
        {{- toYaml .Values.networkPolicy.database.podSelector | nindent 8 }}
  ports:
    - protocol: TCP
      port: {{ .Values.networkPolicy.database.port }}
{{- end }}
{{- range .Values.networkPolicy.database.cidrs }}
- to:
    - ipBlock:
        cidr: {{ . | quote }}
  ports:
    - protocol: TCP
      port: {{ $.Values.networkPolicy.database.port }}
{{- end }}
{{- end }}
