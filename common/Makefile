# Copyright 2019 Tetrate
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

OUTPUT_DIR ?= ../build-image

$(OUTPUT_DIR)/common-context.tar: create_context.py ../envoy_pkg
	@./create_context.py --output $@

.PHONY: clean
clean:
	@rm -rf $(OUTPUT_DIR)/envoy.tar.gz
	@rm -rf $(OUTPUT_DIR)/envoy
	@rm -rf $(OUTPUT_DIR)/common-context.tar
