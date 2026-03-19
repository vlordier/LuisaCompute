#pragma once

namespace luisa {
inline namespace constants {
/// pi
constexpr auto pi = 3.14159265358979323846264338327950288f;
/// pi/2
constexpr auto pi_over_two = 1.57079632679489661923132169163975144f;
/// pi/4
constexpr auto pi_over_four = 0.785398163397448309615660845819875721f;
/// 1/pi
constexpr auto inv_pi = 0.318309886183790671537767526745028724f;
/// 2/pi
constexpr auto two_over_pi = 0.636619772367581343075535053490057448f;
/// sqrt(2)
constexpr auto sqrt_two = 1.41421356237309504880168872420969808f;
/// 1/sqrt(2)
constexpr auto inv_sqrt_two = 0.707106781186547524400844362104849039f;
/// 1-epsilon (largest float less than 1)
constexpr auto one_minus_epsilon = 0x1.fffffep-1f;
/// Euler's number e
constexpr auto e = 2.71828182845904523536028747135266250f;
/// 1/e
constexpr auto inv_e = 0.36787944117144232159552377016146087f;
/// log2(e)
constexpr auto log2_e = 1.44269504088896340735992468100189214f;
/// ln(2)
constexpr auto ln_2 = 0.69314718055994530941723212145817657f;
/// sqrt(3)
constexpr auto sqrt_three = 1.73205080756887729352744634150587237f;
/// 1/sqrt(3)
constexpr auto inv_sqrt_three = 0.57735026918962576450914878050195746f;
/// golden ratio phi = (1 + sqrt(5)) / 2
constexpr auto golden_ratio = 1.61803398874989484820458683436563812f;
}
}// namespace luisa::constants

